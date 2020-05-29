import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager

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
    def get_plugin(self, plugin_id, domain_id):
        pass

    @abstractmethod
    def list_plugins(self, query, domain_id):
        pass

    @abstractmethod
    def stat_plugins(self, query, domain_id):
        pass

    @abstractmethod
    def get_plugin_versions(self, plugin_id, domain_id):
        pass
