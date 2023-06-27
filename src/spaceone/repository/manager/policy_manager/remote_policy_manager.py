import logging
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.repository.model.repository_model import Repository
from spaceone.repository.manager.policy_manager import PolicyManager

__all__ = ['RemotePolicyManager']

_LOGGER = logging.getLogger(__name__)


class RemotePolicyManager(PolicyManager):

    def get_policy(self, repo_vo: Repository, policy_id, domain_id, only=None):
        endpoint = repo_vo.endpoint
        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)
        policy_info = remote_repo_conn.dispatch('Policy.get', {
            'policy_id': policy_id,
            'only': only
        })

        return self.change_response(policy_info, repo_vo, domain_id)

    def list_policies(self, repo_vo: Repository, query: dict, params: dict):
        domain_id = params.get('domain_id')
        endpoint = repo_vo.endpoint
        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)

        response = remote_repo_conn.dispatch('Policy.list', {
            'query': query,
            'repository_id': repo_vo.repository_id
        })

        policies_info = response.get('results', [])
        total_count = response.get('total_count', 0)
        results = []
        for policy_info in policies_info:
            results.append(self.change_response(policy_info, repo_vo, domain_id))

        return results, total_count
