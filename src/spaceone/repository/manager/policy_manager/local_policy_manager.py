import logging

from spaceone.core.error import *
from spaceone.repository.model import *
from spaceone.repository.manager.policy_manager import PolicyManager

__all__ = ['LocalPolicyManager']

_LOGGER = logging.getLogger(__name__)


class LocalPolicyManager(PolicyManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_model: Policy = self.locator.get_model("Policy")

    def create_policy(self, params):
        def _rollback(policy_vo):
            policy_vo.delete()

        policy_vo = self.policy_model.create(params)
        self.transaction.add_rollback(_rollback, policy_vo)

        return policy_vo

    def update_policy(self, params):
        policy_vo = self.get_policy(params['policy_id'], params['domain_id'])
        return self.update_policy_by_vo(params, policy_vo)

    def update_policy_by_vo(self, params, policy_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Policy Data : {old_data["name"]} ({old_data["policy_id"]})')
            policy_vo.update(old_data)

        self.transaction.add_rollback(_rollback, policy_vo.to_dict())
        return policy_vo.update(params)

    def delete_policy(self, policy_id, domain_id):
        policy_vo = self.policy_model.get(domain_id=domain_id, policy_id=policy_id)
        policy_vo.delete()

    def get_policy(self, policy_id, domain_id, only=None):
        # policy_vo = self.policy_model.get(domain_id=domain_id, policy_id=policy_id, only=only)
        policy_vo = self.policy_model.get(policy_id=policy_id, only=only)
        return policy_vo

    def list_policies(self, query, domain_id):
        return self.policy_model.query(**query)

    def stat_policies(self, query, domain_id):
        return self.policy_model.stat(**query)
