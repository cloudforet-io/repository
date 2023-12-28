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
            system_token = config.get_global("TOKEN")
            if not system_token:
                raise ERROR_REMOTE_REPOSITORY_AUTH_FAILURE(key="system_token")

            endpoint = repo_info["endpoint"]
            name = repo_info["name"]

            identity_mgr = self.locator.get_manager("IdentityManager")
            domain_id = identity_mgr.get_domain_id(name)

            _LOGGER.debug(
                f"[list_plugins] Remote Repository domain_id and endpoint: {domain_id} ,{endpoint}"
            )

            remote_repo_conn: SpaceConnector = self.locator.get_connector(
                SpaceConnector, endpoint=endpoint, token=system_token
            )

            response = remote_repo_conn.dispatch(
                "Plugin.list",
                {"query": query, "repository_id": repo_info["repository_id"]},
                x_domain_id=domain_id,
            )

            plugins_info = response.get("results", [])
            total_count = response.get("total_count", 0)
            results = []
            for plugin_info in plugins_info:
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
