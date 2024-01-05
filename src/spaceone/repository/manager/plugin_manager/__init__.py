import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager

__all__ = ["PluginManager"]
_LOGGER = logging.getLogger(__name__)


class PluginManager(BaseManager):
    def register_plugin(self, params):
        pass

    def update_plugin(self, params):
        pass

    def enable_plugin(self, plugin_id, domain_id):
        pass

    def disable_plugin(self, plugin_id, domain_id):
        pass

    def delete_plugin(self, plugin_id, domain_id):
        pass

    @abstractmethod
    def get_plugin(self, repo_info: dict, plugin_id, domain_id):
        pass

    @abstractmethod
    def list_plugins(self, repo_info: dict, query: dict, params: dict):
        pass

    def stat_plugins(self, query):
        pass

    @abstractmethod
    def get_plugin_versions(self, repo_info: dict, plugin_id, domain_id):
        pass

    @staticmethod
    def change_response(
            info: dict, repo_info: dict = None
    ) -> dict:
        if repo_info:
            info["repository_info"] = {
                "repository_id": repo_info["repository_id"],
                "name": repo_info["name"],
                "repository_type": repo_info["repository_type"],
            }

        return info
