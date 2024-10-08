import logging

from spaceone.core.connector.space_connector import SpaceConnector

from spaceone.repository.manager.plugin_manager import PluginManager

__all__ = ["RemotePluginManager"]

_LOGGER = logging.getLogger(__name__)


class RemotePluginManager(PluginManager):
    def get_plugin(self, repo_info: dict, plugin_id: str, domain_id: str = None):
        endpoint = repo_info["endpoint"]
        market_place_token = repo_info["token"]

        remote_repo_conn: SpaceConnector = self.locator.get_connector(
            SpaceConnector, endpoint=endpoint, token=market_place_token
        )

        plugin_info: dict = remote_repo_conn.dispatch(
            "Plugin.get", {"plugin_id": plugin_id, "repository_id": "repo-local"}
        )

        return self.change_response(plugin_info, repo_info)

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
                results.append(self.change_response(plugin_info, repo_info))

            return results, total_count
        except Exception as e:
            _LOGGER.error(f"[list_plugins] {e}")
            return [], 0

    def get_plugin_versions(self, repo_info: dict, plugin_id: str, domain_id: str):
        endpoint = repo_info["endpoint"]
        market_place_token = repo_info["token"]

        remote_repo_conn: SpaceConnector = self.locator.get_connector(
            SpaceConnector, endpoint=endpoint, token=market_place_token
        )
        response = remote_repo_conn.dispatch(
            "Plugin.get_versions",
            {"plugin_id": plugin_id, "repository_id": "repo-local"},
        )

        versions = response.get("results", [])
        total_count = response.get("total_count", 0)

        _LOGGER.debug(f"[get_plugin_version] total version count: {total_count}")

        return versions
