import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager

__all__ = ['PolicyManager']
_LOGGER = logging.getLogger(__name__)


class PolicyManager(BaseManager):

    def create_policy(self, params):
        pass

    def update_policy(self, params):
        pass

    def delete_policy(self, policy_id, domain_id):
        pass

    @abstractmethod
    def get_policy(self, policy_id, domain_id):
        pass

    @abstractmethod
    def list_policies(self, query, domain_id):
        pass

    @abstractmethod
    def stat_policies(self, query, domain_id):
        pass
