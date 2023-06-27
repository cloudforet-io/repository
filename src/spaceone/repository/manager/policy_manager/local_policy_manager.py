import logging

from spaceone.repository.model.policy_model import Policy
from spaceone.repository.model.repository_model import Repository
from spaceone.repository.manager.policy_manager import PolicyManager

__all__ = ['LocalPolicyManager']

_LOGGER = logging.getLogger(__name__)


class LocalPolicyManager(PolicyManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_model: Policy = self.locator.get_model('Policy')

    def create_policy(self, params):
        def _rollback(policy_vo):
            policy_vo.delete()

        policy_vo = self.policy_model.create(params)
        self.transaction.add_rollback(_rollback, policy_vo)

        policy_info = policy_vo.to_dict()
        return self.change_response(policy_info, policy_vo.repository)

    def update_policy(self, params):
        policy_vo = self.policy_model.get(policy_id=params['policy_id'], domain_id=params['domain_id'])
        return self.update_policy_by_vo(params, policy_vo)

    def update_policy_by_vo(self, params, policy_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Policy Data : {old_data["name"]} ({old_data["policy_id"]})')
            policy_vo.update(old_data)

        self.transaction.add_rollback(_rollback, policy_vo.to_dict())

        policy_vo = policy_vo.update(params)
        policy_info = policy_vo.to_dict()
        return self.change_response(policy_info, policy_vo.repository)

    def delete_policy(self, policy_id, domain_id):
        policy_vo = self.policy_model.get(domain_id=domain_id, policy_id=policy_id)
        policy_vo.delete()

    def get_policy(self, repo_vo: Repository, policy_id, domain_id, only=None):
        policy_vo = self.policy_model.get(policy_id=policy_id, domain_id=domain_id, only=only)

        policy_info = policy_vo.to_dict()
        return self.change_response(policy_info, policy_vo.repository)

    def list_policies(self, repo_vo: Repository, query: dict, params: dict):
        domain_id = params.get('domain_id')
        keyword = query.get('keyword')
        query_filter = query.get('filter', [])
        query_filter_or = query.get('filter_or', [])
        query['filter'] = self._append_domain_filter(query_filter, domain_id)
        query['filter_or'] = self._append_keyword_filter(query_filter_or, keyword)

        policy_vos, total_count = self.policy_model.query(**query)
        results = []
        for policy_vo in policy_vos:
            policy_info = policy_vo.to_dict()
            results.append(self.change_response(policy_info, policy_vo.repository))

        return results, total_count

    def stat_policies(self, query):
        return self.policy_model.stat(**query)

    @staticmethod
    def _append_domain_filter(query_filter, domain_id=None):
        if domain_id:
            query_filter.append({
                'k': 'domain_id',
                'v': domain_id,
                'o': 'eq'
            })

        return query_filter

    @staticmethod
    def _append_keyword_filter(query_filter_or, keyword):
        if keyword:
            query_filter_or.append({
                'k': 'name',
                'v': keyword,
                'o': 'contain'
            })

        return query_filter_or
