import logging

from spaceone.core import config
from spaceone.core.connector.space_connector import SpaceConnector

from spaceone.repository.error import *
from spaceone.repository.manager.plugin_manager import PluginManager

__all__ = ["RemotePluginManager"]

_LOGGER = logging.getLogger(__name__)


class RemotePluginManager(PluginManager):
    def get_plugin(self, repo_info: dict, plugin_id: str, domain_id: str):
        endpoint = repo_info["endpoint"]
        remote_repo_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint
        )
        plugin_info: dict = remote_repo_conn.dispatch(
            "Plugin.get", {"plugin_id": plugin_id}
        )

        return self.change_response(plugin_info, repo_info, domain_id)

    def list_plugins(self, repo_info: dict, query: dict, params: dict):
        try:
            endpoint = repo_info["endpoint"]
            market_place_token = repo_info["token"]

            _LOGGER.debug(f"[list_plugins] Remote Repository endpoint: {endpoint}")

            remote_repo_conn: SpaceConnector = self.locator.get_connector(
                SpaceConnector, endpoint=endpoint, token=market_place_token
            )

            response = remote_repo_conn.dispatch(
                "Plugin.list", {"query": query, "repository_id": "repo-local"}
            )

            plugins_info = response.get("results", [])
            total_count = response.get("total_count", 0)
            results = []

            for plugin_info in plugins_info:
                domain_id = plugin_info.get("domain_id")
                results.append(self.change_response(plugin_info, repo_info, domain_id))

            return results, total_count
        except Exception as e:
            _LOGGER.error(f"[list_plugins] {e}")
            return [], 0

    def get_plugin_versions(self, repo_info: dict, plugin_id: str, domain_id: str):
        endpoint = repo_info["endpoint"]
        remote_repo_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint
        )
        response = remote_repo_conn.dispatch(
            "Plugin.get_versions", {"plugin_id": plugin_id}
        )

        versions = response.get("results", [])
        total_count = response.get("total_count", 0)

        _LOGGER.debug(f"[get_plugin_version] total version count: {total_count}")

        return versions
