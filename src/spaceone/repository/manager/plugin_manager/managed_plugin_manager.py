import copy
import logging

from spaceone.core import config
from spaceone.core.error import *
from spaceone.repository.model import Plugin
from spaceone.repository.manager.plugin_manager import PluginManager

from spaceone.repository.manager.identity_manager import IdentityManager

__all__ = ['ManagedPluginManager']

_LOGGER = logging.getLogger(__name__)
_REGISTRY_CONNECTOR_MAP = {
    'DOCKER_HUB': 'DockerHubConnector',
    'AWS_PUBLIC_ECR': 'AWSPublicECRConnector',
    'HARBOR': 'HarborConnector'
}


class ManagedPluginManager(PluginManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_model: Plugin = self.locator.get_model("Plugin")
        identity_mgr = self.locator.get_manager('IdentityManager')
        self.domain_id = identity_mgr.get_root_domain_id()

    def register_plugin(self, params):
        def _rollback(plugin_vo):
            plugin_vo.delete()

        plugin_vo = self.plugin_model.create(params)
        self.transaction.add_rollback(_rollback, plugin_vo)

        return plugin_vo

    def update_plugin(self, params):
        plugin_vo = self.get_plugin(params['plugin_id'], params['domain_id'])
        return self.update_plugin_by_vo(params, plugin_vo)

    def enable_plugin(self, plugin_id, domain_id):
        plugin_vo = self.get_plugin(plugin_id, domain_id)
        return self.update_plugin_by_vo({'state': 'ENABLED'}, plugin_vo)

    def disable_plugin(self, plugin_id, domain_id):
        plugin_vo = self.get_plugin(plugin_id, domain_id)
        return self.update_plugin_by_vo({'state': 'DISABLED'}, plugin_vo)

    def update_plugin_by_vo(self, params, plugin_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Plugin Data : {old_data["name"]} ({old_data["plugin_id"]})')
            plugin_vo.update(old_data)

        self.transaction.add_rollback(_rollback, plugin_vo.to_dict())
        return plugin_vo.update(params)

    def delete_plugin(self, plugin_id, domain_id):
        plugin_vo = self.plugin_model.get(domain_id=domain_id, plugin_id=plugin_id)
        plugin_vo.delete()

    def get_plugin(self, plugin_id, domain_id, only=None):
        plugin_vo = self.plugin_model.get(plugin_id=plugin_id, domain_id=self.domain_id, only=only)

        return plugin_vo

    def list_plugins(self, query):
        new_query = self._change_domain_id(query)
        return self.plugin_model.query(**new_query)

    def stat_plugins(self, query):
        # TODO: may be not working
        return self.plugin_model.stat(**query)

    def get_plugin_versions(self, plugin_id, domain_id):
        """ Get version of image

        version: tag list of docker image
        create RegistryConnector
        call get_tags()

        Returns:
            A list of docker tag
        """
        # We use self.domain_id(root domain) instead of domain_id (user domain)
        plugin_vo: Plugin = self.get_plugin(plugin_id, self.domain_id)
        registry_url = config.get_global('REGISTRY_URL_MAP', {}).get(plugin_vo.registry_type)

        try:
            connector = self.locator.get_connector(_REGISTRY_CONNECTOR_MAP[plugin_vo.registry_type])
            tags = connector.get_tags(registry_url, plugin_vo.image, plugin_vo.registry_config)
        except Exception as e:
            _LOGGER.error(f'[get_plugin_versions] get_tags error: {e}', exc_info=True)
            raise e
        else:
            return tags

    def _change_domain_id(self, query):
        new_query = copy.deepcopy(query)
        q_list = new_query.get('filter', [])
        new_list = []
        appended = False
        for item in q_list:
            if 'k' in item:
                if item['k'] == 'domain_id':
                    new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
                    appended = True
                else:
                    new_list.append(item)
            if 'key' in item:
                if item['key'] == 'domain_id':
                    new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
                    appended = True
                else:
                    new_list.append(item)
 
        if appended == False:
            new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
        new_query['filter'] = new_list
        return new_query
