import logging
import os
import copy
import pandas as pd
import re

from spaceone.core import utils, config
from spaceone.repository.error import *
from spaceone.repository.manager.plugin_manager import PluginManager
from spaceone.repository.model.repository_model import Repository


__all__ = ['ManagedPluginManager']

_LOGGER = logging.getLogger(__name__)
_REGISTRY_CONNECTOR_MAP = {
    'DOCKER_HUB': 'DockerHubConnector',
    'AWS_PRIVATE_ECR': 'AWSPrivateECRConnector',
    'HARBOR': 'HarborConnector'
}
_BASE_DIR = os.path.join(os.path.dirname(__file__), '../../managed_resource/plugin/')
_MANAGED_PLUGINS = []

for filename in os.listdir(_BASE_DIR):
    if filename.endswith('.yaml'):
        file_path = os.path.join(_BASE_DIR, filename)
        plugin_info = utils.load_yaml_from_file(file_path)
        _MANAGED_PLUGINS.append(plugin_info)


class ManagedPluginManager(PluginManager):

    def __init__(self):
        super().__init__()
        self.managed_registry_type = config.get_global('MANAGED_REGISTRY_TYPE', 'DOCKER_HUB')
        self.managed_registry_config = config.get_global('MANAGED_REGISTRY_CONFIG', {})
        self.managed_plugin_image_prefix = config.get_global('MANAGED_PLUGIN_IMAGE_PREFIX', 'cloudforet')
        self.managed_plugin_df = self._load_managed_plugins()

    def get_plugin(self, repo_vo: Repository, plugin_id, domain_id, only=None):
        managed_plugin_df = self._filter_managed_plugins(plugin_id)

        if len(managed_plugin_df) == 0:
            raise ERROR_NOT_FOUND(key='plugin_id', value=plugin_id)

        managed_plugins_info = managed_plugin_df.to_dict('records')

        return self.change_managed_plugin_info(managed_plugins_info[0], repo_vo, domain_id)

    def list_plugins(self, repo_vo: Repository, query: dict, params: dict):
        plugin_id = params.get('plugin_id')
        name = params.get('name')
        service_type = params.get('service_type')
        provider = params.get('provider')
        domain_id = params.get('domain_id')
        sort = query.get('sort', {})
        page = query.get('page', {})
        keyword = query.get('keyword')

        managed_plugin_df = self._filter_managed_plugins(plugin_id, name, service_type, provider, keyword)
        managed_plugin_df = self._sort_managed_plugins(managed_plugin_df, sort)

        total_count = len(managed_plugin_df)
        managed_plugin_df = self._page_managed_plugins(managed_plugin_df, page)

        results = []
        for managed_plugin_info in managed_plugin_df.to_dict('records'):
            results.append(self.change_managed_plugin_info(managed_plugin_info, repo_vo, domain_id))

        return results, total_count

    def get_plugin_versions(self, repo_vo: Repository, plugin_id, domain_id):
        managed_plugin_info = self.get_plugin(repo_vo, plugin_id, domain_id)
        registry_type = managed_plugin_info['registry_type']
        registry_config = managed_plugin_info['registry_config']
        image = managed_plugin_info['image']

        registry_url = config.get_global('REGISTRY_URL_MAP', {}).get(registry_type)
        registry_connector = _REGISTRY_CONNECTOR_MAP[registry_type]

        try:
            connector = self.locator.get_connector(registry_connector)
            tags = connector.get_tags(registry_url, image, registry_config)
        except Exception as e:
            _LOGGER.error(f'[get_plugin_versions] get_tags error: {e}', exc_info=True)
            raise e
        else:
            return tags


    @staticmethod
    def _load_managed_plugins():
        managed_plugin_df = pd.DataFrame(copy.deepcopy(_MANAGED_PLUGINS))
        return managed_plugin_df.fillna('')

    def _filter_managed_plugins(self, plugin_id=None, name=None, service_type=None, provider=None, keyword=None):
        managed_plugin_df = copy.deepcopy(self.managed_plugin_df)

        if plugin_id:
            managed_plugin_df = managed_plugin_df[managed_plugin_df['plugin_id'] == plugin_id]

        if name:
            managed_plugin_df = managed_plugin_df[managed_plugin_df['name'] == name]

        if service_type:
            managed_plugin_df = managed_plugin_df[managed_plugin_df['service_type'] == service_type]

        if provider:
            managed_plugin_df = managed_plugin_df[managed_plugin_df['provider'] == provider]

        if keyword:
            managed_plugin_df = managed_plugin_df[
                managed_plugin_df['name'].str.contains(keyword, flags=re.IGNORECASE)]

        return managed_plugin_df

    @staticmethod
    def _sort_managed_plugins(managed_plugin_df: pd.DataFrame, sort: dict):
        if sort_key := sort.get('key'):
            desc = sort.get('desc', False)
            try:
                return managed_plugin_df.sort_values(by=sort_key, ascending=not desc)
            except Exception as e:
                raise ERROR_SORT_KEY(sort_key=sort_key)
        else:
            return managed_plugin_df

    @staticmethod
    def _page_managed_plugins(managed_plugin_df: pd.DataFrame, page: dict):
        if limit := page.get('limit'):
            start = page.get('start', 1) - 1
            return managed_plugin_df[start:start + limit]
        else:
            return managed_plugin_df

    def change_managed_plugin_info(self, plugin_info, repo_vo, domain_id):
        plugin_info['state'] = 'ENABLED'
        plugin_info['registry_type'] = self.managed_registry_type
        plugin_info['registry_config'] = self.managed_registry_config
        plugin_info['image'] = f"{self.managed_plugin_image_prefix}/{plugin_info['image']}"

        if repo_vo:
            plugin_info['repository_info'] = {
                'repository_id': repo_vo.repository_id,
                'name': repo_vo.name,
                'repository_type': repo_vo.repository_type,
            }

        if domain_id:
            plugin_info['domain_id'] = domain_id

        return plugin_info
