import logging
import jsonschema

from spaceone.core.service import *

from spaceone.repository.error import *
from spaceone.repository.manager.identity_manager import IdentityManager
from spaceone.repository.manager.schema_manager.local_schema_manager import LocalSchemaManager
from spaceone.repository.manager.schema_manager.remote_schema_manager import RemoteSchemaManager
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler(exclude=['get'])
@authorization_handler
@event_handler
class SchemaService(BaseService):

    @transaction
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
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            schema_vo (object)
        """

        # Pre-condition Check
        self._check_schema(params['schema'])
        self._check_project(params.get('project_id'), params['domain_id'])
        self._check_service_type(params.get('service_type'))

        schema_mgr: LocalSchemaManager = self.locator.get_manager('LocalSchemaManager')

        # Only LOCAL repository can be registered
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        params['repository'] = repo_mgr.get_local_repository()

        return schema_mgr.register_schema(params)

    @transaction
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
            schema_vo (object)
        """
        # Pre-condition Check
        self._check_schema(params.get('schema'))
        self._check_project(params.get('project_id'), params['domain_id'])
        self._check_service_type(params.get('service_type'))

        schema_mgr: LocalSchemaManager = self.locator.get_manager('LocalSchemaManager')
        return schema_mgr.update_schema(params)

    @transaction
    @check_required(['name', 'domain_id'])
    def delete(self, params):
        """Delete Schema (local repo only)

        Args:
            params (dict): {
                'name': 'str',
                'domain_id': 'str'
            }

        Returns:
            schema_vo (object)
        """
        schema_name = params['name']
        domain_id = params['domain_id']

        schema_mgr: LocalSchemaManager = self.locator.get_manager('LocalSchemaManager')
        return schema_mgr.delete_schema(schema_name, domain_id)

    @transaction
    @check_required(['name', 'domain_id'])
    def get(self, params):
        """ Get Schema (local & remote)

        Args:
            params (dict): {
                'schema_id': 'str',
                'repository_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            schema_vo (object)
        """
        schema_name = params['name']
        domain_id = params['domain_id']
        repo_id = params.get('repository_id')
        only = params.get('only')

        repo_vos = self._list_repositories(repo_id)
        for repo_vo in repo_vos:
            _LOGGER.debug(f'[get] find at name: {repo_vo.name} '
                          f'repo_type: {repo_vo.repository_type}')
            schema_mgr = self._get_schema_manager_by_repo(repo_vo)
            try:
                schema_vo = schema_mgr.get_schema(schema_name, domain_id, only)
            except Exception as e:
                schema_vo = None

            if schema_vo:
                return schema_vo

        raise ERROR_NO_SCHEMA(name=schema_name)

    @transaction
    @check_required(['repository_id', 'domain_id'])
    @append_query_filter(['repository_id', 'name', 'service_type', 'project_id', 'domain_id'])
    @append_keyword_filter(['name', 'labels'])
    def list(self, params):
        """ List schemas (local or repo)

        Args:
            params (dict): {
                'repository_id': 'str',
                'name': 'str',
                'service_type': 'str',
                'project_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            schemas_vo (object)
            total_count
        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repository_id = params['repository_id']
        repo_vo = repo_mgr.get_repository(repository_id)

        schema_mgr = self._get_schema_manager_by_repo(repo_vo)
        query = params.get('query', {})
        return schema_mgr.list_schemas(query, params['domain_id'])

    @transaction
    @check_required(['query', 'repository_id', 'domain_id'])
    @append_query_filter(['repository_id', 'domain_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repository_id = params['repository_id']
        repo_vo = repo_mgr.get_repository(repository_id)

        schema_mgr = self._get_schema_manager_by_repo(repo_vo)
        query = params.get('query', {})
        return schema_mgr.stat_schemas(query, params['domain_id'])

    def _get_schema_manager_by_repo(self, repo):
        if repo.repository_type == 'local':
            local_schema_mgr: LocalSchemaManager = self.locator.get_manager('LocalSchemaManager', repository=repo)
            return local_schema_mgr
        else:
            remote_schema_mgr: RemoteSchemaManager = self.locator.get_manager('RemoteSchemaManager', repository=repo)
            return remote_schema_mgr

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
            identity.domain
            inventory.collector

        Raises:
            ERROR_INVALID_PARAMETER
        """
        if name:
            pass
            # idx = name.split('.')
            # if len(idx) != 2:
            #     raise ERROR_INVALID_PARAMETER(key='service_type', reason=f'{name} format is invalid.')

    def _check_project(self, project_id, domain_id):
        if project_id:
            identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
            identity_mgr.get_project(project_id, domain_id)

    def _list_repositories(self, repository_id):
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        query = {
            'sort': {
                'key': 'repository_type'
            }
        }

        if repository_id:
            query.update({'repository_id': repository_id})

        repo_vos, total_count = repo_mgr.list_repositories(query)
        _LOGGER.debug(f'[_list_repositories] Number of repositories: {total_count}')

        if total_count == 0:
            raise ERROR_NO_REPOSITORY()

        return repo_vos
