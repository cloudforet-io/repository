import logging
import jsonschema

from spaceone.core.service import *

from spaceone.repository.error import *
from spaceone.repository.manager.schema_manager.local_schema_manager import LocalSchemaManager
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler(exclude=['get'])
@authorization_handler(exclude=['get'])
@mutation_handler
@event_handler
class SchemaService(BaseService):

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'service_type', 'schema', 'domain_id'])
    def create(self, params):
        """Create Schema

        Args:
            params (dict): {
                'name': 'str',
                'service_type': 'str',
                'schema': 'dict',
                'labels': 'list',
                'tags': 'dict',
                'project_id': 'str', // deprecated
                'domain_id': 'str'
            }

        Returns:
            schema_info (dict)
        """

        # Pre-condition Check
        self._check_schema(params['schema'])
        self._check_service_type(params.get('service_type'))

        schema_mgr: LocalSchemaManager = self.locator.get_manager('LocalSchemaManager')

        # Only LOCAL repository can be registered
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        params['repository'] = repo_mgr.get_local_repository()
        params['repository_id'] = params['repository'].repository_id

        return schema_mgr.register_schema(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'domain_id'])
    def update(self, params):
        """Update Schema. (local repo only)

        Args:
            params (dict): {
                'name': 'str',
                'schema': 'dict',
                'labels': 'list',
                'tags': 'dict'
                'domain_id': 'str'
            }

        Returns:
            schema_info (dict)
        """

        # Pre-condition Check
        self._check_schema(params.get('schema'))
        self._check_service_type(params.get('service_type'))

        schema_mgr: LocalSchemaManager = self.locator.get_manager('LocalSchemaManager')
        return schema_mgr.update_schema(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'domain_id'])
    def delete(self, params):
        """Delete Schema (local repo only)

        Args:
            params (dict): {
                'name': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """
        schema_name = params['name']
        domain_id = params['domain_id']

        schema_mgr: LocalSchemaManager = self.locator.get_manager('LocalSchemaManager')
        return schema_mgr.delete_schema(schema_name, domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name'])
    @change_only_key({'repository_info': 'repository'})
    def get(self, params):
        """ Get Schema (all repositories)

        Args:
            params (dict): {
                'name': 'str',
                'repository_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            schema_vo (object)
        """

        schema_name = params['name']
        domain_id = params.get('domain_id')
        repo_id = params.get('repository_id')
        only = params.get('only')

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repo_vos = repo_mgr.get_all_repositories(repo_id)

        for repo_vo in repo_vos:
            _LOGGER.debug(f'[get] find at name: {repo_vo.name} '
                          f'(repo_type: {repo_vo.repository_type})')
            schema_mgr = self._get_schema_manager_by_repo(repo_vo.repository_type)
            try:
                return schema_mgr.get_schema(repo_vo, schema_name, domain_id, only)
            except Exception as e:
                _LOGGER.debug(f'[get] Can not find schema({schema_name}) at {repo_vo.name}')

        raise ERROR_NO_SCHEMA(name=schema_name)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['repository_id'])
    @change_only_key({'repository_info': 'repository'}, key_path='query.only')
    @append_query_filter(['repository_id', 'name', 'service_type'])
    def list(self, params):
        """ List schemas (specific repository)

        Args:
            params (dict): {
                'repository_id': 'str',
                'name': 'str',
                'service_type': 'str',
                'project_id': 'str', // deprecated
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of schema_info'
            total_count (int)
        """

        query = params.get('query', {})

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repository_id = params['repository_id']
        repo_vo = repo_mgr.get_repository(repository_id)

        schema_mgr = self._get_schema_manager_by_repo(repo_vo.repository_type)

        return schema_mgr.list_schemas(repo_vo, query, params)

    def _get_schema_manager_by_repo(self, repository_type):
        if repository_type == 'local':
            return self.locator.get_manager('LocalSchemaManager')
        elif repository_type == 'managed':
            return self.locator.get_manager('ManagedSchemaManager')
        else:
            return self.locator.get_manager('RemoteSchemaManager')

    @staticmethod
    def _check_schema(schema):
        """
        Check json schema
        """
        if schema:
            try:
                jsonschema.Draft7Validator.check_schema(schema)
            except Exception as e:
                raise ERROR_INVALID_SCHEMA(key='schema')

    @staticmethod
    def _check_service_type(name):
        """
        service_type has format rule
        format:
            <service>.<purpose>
        example:
            identity.Domain
            inventory.Collector

        Raises:
            ERROR_INVALID_PARAMETER
        """
        pass
