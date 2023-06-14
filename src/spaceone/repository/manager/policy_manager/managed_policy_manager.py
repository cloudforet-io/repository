import copy
import logging

from spaceone.core.error import *
from spaceone.repository.model import *
from spaceone.repository.manager.policy_manager import PolicyManager

from spaceone.repository.manager.identity_manager import IdentityManager

__all__ = ['ManagedPolicyManager']

_LOGGER = logging.getLogger(__name__)


class ManagedPolicyManager(PolicyManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_model: Policy = self.locator.get_model("Policy")
        identity_mgr = self.locator.get_manager('IdentityManager')
        self.domain_id = identity_mgr.get_root_domain_id()

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
        policy_vo = self.policy_model.get(policy_id=policy_id, domain_id=self.domain_id, only=only)

        return policy_vo

    def list_policies(self, query):
        new_query = self._change_domain_id(query)
        return self.policy_model.query(**new_query)

    def stat_policies(self, query):
        return self.policy_model.stat(**query)

    def _change_domain_id(self, query):
        new_query = copy.deepcopy(query)
        q_list = new_query.get('filter', [])
        new_list = []
        appended = False
        for item in q_list:
            if 'k' in item:
                if item['k'] == 'domain_id':
                    new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
                    appended = True
                else:
                    new_list.append(item)
            if 'key' in item:
                if item['key'] == 'domain_id':
                    new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
                    appended = True
                else:
                    new_list.append(item)
 
        if appended == False:
            new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
        new_query['filter'] = new_list
        return new_query
