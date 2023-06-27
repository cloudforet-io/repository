import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager
from spaceone.repository.model.repository_model import Repository

__all__ = ['PluginManager']
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
    def get_plugin(self, repo_vo: Repository, plugin_id, domain_id, only=None):
        pass

    @abstractmethod
    def list_plugins(self, repo_vo: Repository, query: dict, params: dict):
        pass

    def stat_plugins(self, query):
        pass

    @abstractmethod
    def get_plugin_versions(self, repo_vo: Repository, plugin_id, domain_id):
        pass

    @staticmethod
    def change_response(info, repo_vo: Repository = None, domain_id: str = None):
        if repo_vo:
            info['repository_info'] = {
                'repository_id': repo_vo.repository_id,
                'name': repo_vo.name,
                'repository_type': repo_vo.repository_type,
            }

        if domain_id:
            info['domain_id'] = domain_id

        return info
