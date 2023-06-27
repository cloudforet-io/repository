import logging
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.repository.model.repository_model import Repository
from spaceone.repository.manager.plugin_manager import PluginManager

__all__ = ['RemotePluginManager']

_LOGGER = logging.getLogger(__name__)


class RemotePluginManager(PluginManager):

    def get_plugin(self, repo_vo: Repository, plugin_id, domain_id, only=None):
        endpoint = repo_vo.endpoint
        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)
        plugin_info = remote_repo_conn.dispatch('Plugin.get', {
            'plugin_id': plugin_id,
            'only': only
        })

        return self.change_response(plugin_info, repo_vo, domain_id)

    def list_plugins(self, repo_vo: Repository, query: dict, params: dict):
        domain_id = params.get('domain_id')
        endpoint = repo_vo.endpoint
        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)

        response = remote_repo_conn.dispatch('Plugin.list', {
            'query': query,
            'repository_id': repo_vo.repository_id
        })

        plugins_info = response.get('results', [])
        total_count = response.get('total_count', 0)
        results = []
        for plugin_info in plugins_info:
            results.append(self.change_response(plugin_info, repo_vo, domain_id))

        return results, total_count

    def get_plugin_versions(self, repo_vo: Repository, plugin_id, domain_id):
        endpoint = repo_vo.endpoint
        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)
        response = remote_repo_conn.dispatch('Plugin.get_versions', {
            'plugin_id': plugin_id
        })

        versions = response.get('results', [])
        total_count = response.get('total_count', 0)

        _LOGGER.debug(f'[get_plugin_version] total version count: {total_count}')

        return versions
