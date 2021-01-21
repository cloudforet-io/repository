import logging
import jsonschema

from spaceone.core.service import *

from spaceone.repository.error import *
from spaceone.repository.model.capability_model import Capability
from spaceone.repository.manager.identity_manager import IdentityManager
from spaceone.repository.manager.plugin_manager.local_plugin_manager import LocalPluginManager
from spaceone.repository.manager.plugin_manager.remote_plugin_manager import RemotePluginManager
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler(exclude=['get', 'get_versions'])
@authorization_handler
@event_handler
class PluginService(BaseService):

    @transaction
    @check_required(['name', 'service_type', 'image', 'domain_id'])
    def register(self, params):
        """Register Plugin (local repo only)

        Args:
            params (dict): {
                'name': 'str',
                'service_type': 'str',
                'image': 'str',
                'provider': 'str',
                'capability': 'dict',
                'template': 'dict',
                'labels': 'list',
                'tags': 'list',
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            plugin_vo (object)
        """

        # Pre-condition Check
        self._check_template(params.get('template'))
        # self._check_capability(params.get('capability'))
        self._check_project(params.get('project_id'), params['domain_id'])
        self._check_service_type(params.get('service_type'))

        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')

        # Only LOCAL repository can be registered
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        params['repository'] = repo_mgr.get_local_repository()
        params['repository_id'] = params['repository'].repository_id

        return plugin_mgr.register_plugin(params)

    @transaction
    @check_required(['plugin_id', 'domain_id'])
    def update(self, params):
        """Update Plugin. (local repo only)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'name': 'str',
                'capability': 'dict',
                'template': 'dict',
                'labels': 'list',
                'tags': 'list'
                'domain_id': 'str'
            }

        Returns:
            plugin_vo (object)
        """
        # Pre-condition Check
        self._check_template(params.get('template'))
        # self._check_capability(params.get('capability'))
        self._check_service_type(params.get('service_type'))

        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.update_plugin(params)

    @transaction
    @check_required(['plugin_id', 'domain_id'])
    def deregister(self, params):
        """Deregister Plugin (local repo only)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            plugin_vo (object)
        """
        plugin_id = params['plugin_id']
        domain_id = params['domain_id']

        #########################################################################
        # Warning 
        #
        # To degister plugin, plugin has to verify there is no installed plugins
        # If there was installed plugin, other micro service can query endpoint
        # But plugin can not reply endpoint
        ##########################################################################
        # TODO: check plugin is not used

        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.delete_plugin(plugin_id, domain_id)

    @transaction
    @check_required(['plugin_id', 'domain_id'])
    def enable(self, params):
        """ Enable plugin (local repo only)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            plugin_vo (object)
        """
        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.enable_plugin(params['plugin_id'], params['domain_id'])

    @transaction
    @check_required(['plugin_id', 'domain_id'])
    def disable(self, params):
        """ Disable Plugin (local repo only)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            plugin_vo (object)
        """
        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.disable_plugin(params['plugin_id'], params['domain_id'])

    @transaction
    @check_required(['plugin_id', 'domain_id'])
    def get_versions(self, params):
        """ Get Plugin version (local & remote)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'repository_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            version_list (list)
        """

        plugin_id = params['plugin_id']
        domain_id = params['domain_id']
        repo_id = params.get('repository_id', None)

        repo_vos = self._list_repositories(repo_id)
        for repo_vo in repo_vos:
            plugin_mgr = self._get_plugin_manager_by_repo(repo_vo)
            # plugin_manager may emit Error, if it is not found
            # skip error
            try:
                _LOGGER.debug(f'[get_versions] find at name: {repo_vo.name} '
                              f'repo_type: {repo_vo.repository_type}')
                version_list = plugin_mgr.get_plugin_versions(plugin_id, domain_id)
            except Exception as e:
                version_list = None

            if version_list:
                _LOGGER.debug(f'[get_versions] version_list: {version_list}')
                # User wants reverse list
                version_list.sort(reverse=True)
                _LOGGER.debug(f'[get_versions] sorted version_list: {version_list}')
                return version_list

        _LOGGER.error(f'[get_versions] no version: {plugin_id}')
        raise ERROR_NO_PLUGIN(plugin_id=plugin_id)

    @transaction
    @check_required(['plugin_id', 'domain_id'])
    @change_only_key({'repository_info': 'repository'})
    def get(self, params):
        """ Get Plugin (local & remote)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'repository_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            plugin_vo (object)
        """
        plugin_id = params['plugin_id']
        domain_id = params['domain_id']
        repo_id = params.get('repository_id')
        only = params.get('only')

        repo_vos = self._list_repositories(repo_id)
        for repo_vo in repo_vos:
            _LOGGER.debug(f'[get] find at name: {repo_vo.name} '
                          f'repo_type: {repo_vo.repository_type}')
            plugin_mgr = self._get_plugin_manager_by_repo(repo_vo)
            try:
                plugin_vo = plugin_mgr.get_plugin(plugin_id, domain_id, only)
            except Exception as e:
                plugin_vo = None

            if plugin_vo:
                return plugin_vo

        raise ERROR_NO_PLUGIN(plugin_id=plugin_id)

    @transaction
    @check_required(['repository_id', 'domain_id'])
    @change_only_key({'repository_info': 'repository'}, key_path='query.only')
    @append_query_filter(['repository_id', 'plugin_id', 'name', 'state', 'service_type',
                          'provider', 'project_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['plugin_id', 'name', 'provider', 'labels'])
    def list(self, params):
        """ List plugins (local or repo)

        Args:
            params (dict): {
                'repository_id': 'str',
                'plugin_id': 'str',
                'name': 'str',
                'state': 'str',
                'service_type': 'str',
                'provider': 'str',
                'project_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            plugins_vo (object)
            total_count
        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repository_id = params['repository_id']
        repo_vo = repo_mgr.get_repository(repository_id)

        plugin_mgr = self._get_plugin_manager_by_repo(repo_vo)
        query = params.get('query', {})

        # Temporary code for DB migration
        if 'only' in query:
            query['only'] += ['repository_id']

        return plugin_mgr.list_plugins(query, params['domain_id'])

    @transaction
    @check_required(['query', 'repository_id', 'domain_id'])
    @append_query_filter(['repository_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['plugin_id', 'name', 'provider', 'labels'])
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

        plugin_mgr = self._get_plugin_manager_by_repo(repo_vo)
        query = params.get('query', {})
        return plugin_mgr.stat_plugins(query, params['domain_id'])

    def _get_plugin_manager_by_repo(self, repo):
        if repo.repository_type == 'local':
            local_plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager', repository=repo)
            return local_plugin_mgr
        else:
            remote_plugin_mgr: RemotePluginManager = self.locator.get_manager('RemotePluginManager', repository=repo)
            return remote_plugin_mgr

    @staticmethod
    def _check_template(template):
        """
        Check json schema
        """
        if template:
            for key, value in template.items():
                if isinstance(value, dict) and 'schema' in value:
                    try:
                        jsonschema.Draft7Validator.check_schema(value['schema'])
                    except Exception as e:
                        raise ERROR_INVALID_TEMPLATE_SCHEMA(key=f'template.{key}')

    @staticmethod
    def _check_capability(capability):
        if capability:
            try:
                capability_vo = Capability(capability)
                capability_vo.validate()
            except Exception as e:
                raise ERROR_INVALID_PARAMETER(key='capability', reason=e)

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
        query = {}
        if repository_id:
            query.update({'repository_id': repository_id})

        repo_vos, total_count = repo_mgr.list_repositories(query)
        _LOGGER.debug(f'[_list_repositories] Number of repositories: {total_count}')

        if total_count == 0:
            raise ERROR_NO_REPOSITORY()

        return repo_vos
