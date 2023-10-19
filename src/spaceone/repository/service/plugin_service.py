import copy
import logging
import jsonschema
import re

from spaceone.core.service import *
from spaceone.core import config

from spaceone.repository.error import *
from spaceone.repository.model.capability_model import Capability
from spaceone.repository.manager.plugin_manager.local_plugin_manager import LocalPluginManager
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)

MAX_IMAGE_NAME_LENGTH = 48
REGISTRY_MAP = {
    "DOCKER_HUB": "DockerHubConnector",
    "AWS_PRIVATE_ECR": "AWSPrivateECRConnector",
    "HARBOR": "HarborConnector"
}


@authentication_handler(exclude=['get', 'get_versions'])
@authorization_handler(exclude=['get', 'get_versions'])
@mutation_handler
@event_handler
class PluginService(BaseService):

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'service_type', 'image', 'domain_id'])
    def register(self, params):
        """Register Plugin (local repo only)

        Args:
            params (dict): {
                'name': 'str',
                'service_type': 'str',
                'registry_type': 'str',
                'registry_config': 'dict',
                'image': 'str',
                'provider': 'str',
                'capability': 'dict',
                'template': 'dict',
                'labels': 'list',
                'tags': 'dict',
                'project_id': 'str', // deprecated
                'domain_id': 'str'
            }

        Returns:
            plugin_info (dict)
        """

        registry_type = params.get('registry_type', 'DOCKER_HUB')
        registry_config = params.get('registry_config', {})
        image = params['image']
        plugin_id = self._get_image_name(image)

        # Pre-condition Check
        self._check_template(params.get('template'))
        # self._check_capability(params.get('capability'))
        self._check_service_type(params.get('service_type'))
        self._check_image(image)
        self._check_registry_type(registry_type)
        self._check_registry_config(registry_type, registry_config)

        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        
        # Only LOCAL repository can be registered
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        params['plugin_id'] = plugin_id
        params['repository'] = repo_mgr.get_local_repository()
        params['repository_id'] = params['repository'].repository_id

        return plugin_mgr.register_plugin(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
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
                'tags': 'dict'
                'domain_id': 'str'
            }

        Returns:
            plugin_info (dict)
        """

        # Pre-condition Check
        self._check_template(params.get('template'))
        # self._check_capability(params.get('capability'))
        self._check_service_type(params.get('service_type'))

        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.update_plugin(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['plugin_id', 'domain_id'])
    def deregister(self, params):
        """Deregister Plugin (local repo only)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        #########################################################################
        # Warning 
        #
        # To deregister plugin, plugin has to verify there is no installed plugins
        # If there was installed plugin, other micro service can query endpoint
        # But plugin can not reply endpoint
        ##########################################################################
        # TODO: check plugin is not used

        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.delete_plugin(params['plugin_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['plugin_id', 'domain_id'])
    def enable(self, params):
        """ Enable plugin (local repo only)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            plugin_info (dict)
        """

        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.enable_plugin(params['plugin_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['plugin_id', 'domain_id'])
    def disable(self, params):
        """ Disable Plugin (local repo only)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            plugin_info (dict)
        """
        plugin_mgr: LocalPluginManager = self.locator.get_manager('LocalPluginManager')
        return plugin_mgr.disable_plugin(params['plugin_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['plugin_id'])
    def get_versions(self, params):
        """ Get Plugin version (all repositories)

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
        domain_id = params.get('domain_id')
        repo_id = params.get('repository_id')

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repo_vos = repo_mgr.get_all_repositories(repo_id)

        for repo_vo in repo_vos:
            _LOGGER.debug(f'[get] find at name: {repo_vo.name} '
                          f'(repo_type: {repo_vo.repository_type})')
            plugin_mgr = self._get_plugin_manager_by_repo(repo_vo.repository_type)
            try:
                return plugin_mgr.get_plugin_versions(repo_vo, plugin_id, domain_id)
            except Exception as e:
                _LOGGER.debug(f'[get_versions] Cannot find plugin: {plugin_id} at {repo_vo.name}')

        raise ERROR_NO_PLUGIN(plugin_id=plugin_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['plugin_id'])
    @change_only_key({'repository_info': 'repository'})
    def get(self, params):
        """ Get Plugin (all repositories)

        Args:
            params (dict): {
                'plugin_id': 'str',
                'repository_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            plugin_info (dict)
        """

        plugin_id = params['plugin_id']
        domain_id = params.get('domain_id')
        repo_id = params.get('repository_id')
        only = params.get('only')

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repo_vos = repo_mgr.get_all_repositories(repo_id)

        for repo_vo in repo_vos:
            _LOGGER.debug(f'[get] find at name: {repo_vo.name} '
                          f'(repo_type: {repo_vo.repository_type})')
            plugin_mgr = self._get_plugin_manager_by_repo(repo_vo.repository_type)
            try:
                return plugin_mgr.get_plugin(repo_vo, plugin_id, domain_id, only)
            except Exception as e:
                _LOGGER.debug(f'[get] Can not find plugin({plugin_id}) at {repo_vo.name}')

        raise ERROR_NO_PLUGIN(plugin_id=plugin_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @change_only_key({'repository_info': 'repository'}, key_path='query.only')
    @append_query_filter(['repository_id', 'plugin_id', 'name', 'state', 'service_type',
                          'registry_type', 'provider'])
    def list(self, params):
        """ List plugins (all repositories)

        Args:
            params (dict): {
                'repository_id': 'str',
                'plugin_id': 'str',
                'name': 'str',
                'state': 'str',
                'service_type': 'str',
                'registry_type': 'str',
                'provider': 'str',
                'project_id': 'str', // deprecated
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of plugin_info'
            total_count (int)
        """

        query = params.get('query', {})
        query['only'] = query.get('only', [])

        if 'registry_url' in query['only']:
            query['only'].remove('registry_url')

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        if repository_id := params.get('repository_id'):

            repo_vo = repo_mgr.get_repository(repository_id)

            plugin_mgr = self._get_plugin_manager_by_repo(repo_vo.repository_type)

            return plugin_mgr.list_plugins(repo_vo, query, params)
        else:
            all_plugins_info = []
            plugin_total_count = 0
            query_page = None
            if 'page' in query:
                query_page = query['page']
                del query['page']

            repo_vos = repo_mgr.get_all_repositories()
            for repo_vo in repo_vos:
                plugin_mgr = self._get_plugin_manager_by_repo(repo_vo.repository_type)
                plugins_info, total_count = plugin_mgr.list_plugins(repo_vo, copy.deepcopy(query), params)
                all_plugins_info += plugins_info
                plugin_total_count += total_count

            if query_page:
                page_start = query_page.get('start', 1) - 1
                page_limit = query_page.get('limit')

                if page_limit:
                    all_plugins_info = all_plugins_info[page_start:page_start+page_limit]

            return all_plugins_info, plugin_total_count

    def _get_plugin_manager_by_repo(self, repository_type):
        if repository_type == 'local':
            return self.locator.get_manager('LocalPluginManager')
        elif repository_type == 'managed':
            return self.locator.get_manager('ManagedPluginManager')
        else:
            return self.locator.get_manager('RemotePluginManager')

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
            identity.Domain
            inventory.Collector

        Raises:
            ERROR_INVALID_PARAMETER
        """
        if name:
            pass
            # idx = name.split('.')
            # if len(idx) != 2:
            #     raise ERROR_INVALID_PARAMETER(key='service_type', reason=f'{name} format is invalid.')

    @staticmethod
    def _get_image_name(image):
        return image.rsplit('/', 1)[-1]

    @staticmethod
    def _check_registry_type(registry_type):
        registry_url = config.get_global('REGISTRY_URL_MAP', {}).get(registry_type)

        if registry_url.strip() == '':
            raise ERROR_REGISTRY_SETTINGS(registry_type=registry_type)

    @staticmethod
    def _check_registry_config(registry_type, registry_config):
        if registry_type == 'AWS_PRIVATE_ECR':
            if 'account_id' not in registry_config:
                raise ERROR_REQUIRED_PARAMETER(key='registry_config.account_id')

    def _check_image(self, image):
        """ Check image name
        format: repository/image_name
        length of image_name: < 40
        format of image_name: string and - (underscore is not allowed)
        """
        _LOGGER.debug(f'[_check_image] {image}')
        image_name = self._get_image_name(image)

        # check image_name length
        if len(image_name) > MAX_IMAGE_NAME_LENGTH:
            raise ERROR_INVALID_IMAGE_LENGTH(name=image_name, length=MAX_IMAGE_NAME_LENGTH)

        # Search naming format
        m = re.search('(?![a-zA-Z0-9\-]).*', image_name)
        if m:
            if len(m.group()) > 1:
                raise ERROR_INVALID_IMAGE_NAME_FORMAT(name=image_name)
            return True

        raise ERROR_INVALID_IMAGE_NAME_FORMAT(name=image_name)
