import logging
import os
import copy
import pandas as pd
import re

from spaceone.core import utils
from spaceone.repository.error import *
from spaceone.repository.manager.policy_manager import PolicyManager
from spaceone.repository.model.repository_model import Repository


__all__ = ['ManagedPolicyManager']

_LOGGER = logging.getLogger(__name__)
_BASE_DIR = os.path.join(os.path.dirname(__file__), '../../managed_resource/policy/')
_MANAGED_POLICIES = []

for filename in os.listdir(_BASE_DIR):
    if filename.endswith('.yaml'):
        file_path = os.path.join(_BASE_DIR, filename)
        policy_info = utils.load_yaml_from_file(file_path)
        _MANAGED_POLICIES.append(policy_info)


class ManagedPolicyManager(PolicyManager):

    def __init__(self):
        super().__init__()
        self.managed_policy_df = self._load_managed_policies()

    def get_policy(self, repo_vo: Repository, policy_id, domain_id, only=None):
        managed_policy_df = self._filter_managed_policies(policy_id)

        if len(managed_policy_df) == 0:
            raise ERROR_NOT_FOUND(key='policy_id', value=policy_id)

        managed_policies_info = managed_policy_df.to_dict('records')

        return self.change_response(managed_policies_info[0], repo_vo, domain_id)

    def list_policies(self, repo_vo: Repository, query: dict, params: dict):
        policy_id = params.get('policy_id')
        name = params.get('name')
        domain_id = params.get('domain_id')
        sort = query.get('sort', {})
        page = query.get('page', {})
        keyword = query.get('keyword')

        managed_policy_df = self._filter_managed_policies(policy_id, name, keyword)
        managed_policy_df = self._sort_managed_policies(managed_policy_df, sort)

        total_count = len(managed_policy_df)
        managed_policy_df = self._page_managed_policies(managed_policy_df, page)

        results = []
        for managed_policy_info in managed_policy_df.to_dict('records'):
            results.append(self.change_response(managed_policy_info, repo_vo, domain_id))

        return results, total_count

    @staticmethod
    def _load_managed_policies():
        return pd.DataFrame(_MANAGED_POLICIES)

    def _filter_managed_policies(self, policy_id=None, name=None, keyword=None):
        managed_policy_df = copy.deepcopy(self.managed_policy_df)

        if policy_id:
            managed_policy_df = managed_policy_df[managed_policy_df['policy_id'] == policy_id]

        if name:
            managed_policy_df = managed_policy_df[managed_policy_df['name'] == name]

        if keyword:
            managed_policy_df = managed_policy_df[
                managed_policy_df['name'].str.contains(keyword, flags=re.IGNORECASE)]

        return managed_policy_df

    @staticmethod
    def _sort_managed_policies(managed_policy_df: pd.DataFrame, sort: dict):
        if sort_key := sort.get('key'):
            desc = sort.get('desc', False)
            try:
                return managed_policy_df.sort_values(by=sort_key, ascending=not desc)
            except Exception as e:
                raise ERROR_SORT_KEY(sort_key=sort_key)
        else:
            return managed_policy_df

    @staticmethod
    def _page_managed_policies(managed_policy_df: pd.DataFrame, page: dict):
        if limit := page.get('limit'):
            start = page.get('start', 1) - 1
            return managed_policy_df[start:start + limit]
        else:
            return managed_policy_df
