import logging
import re

from spaceone.core.service import *
from spaceone.core import utils

from spaceone.repository.error import *
from spaceone.repository.model.capability_model import Capability
from spaceone.repository.manager.identity_manager import IdentityManager
from spaceone.repository.manager.policy_manager.local_policy_manager import LocalPolicyManager
from spaceone.repository.manager.policy_manager.remote_policy_manager import RemotePolicyManager
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)

MAX_POLICY_ID_LENGTH = 48


@authentication_handler(exclude=['get'])
@authorization_handler(exclude=['get'])
@mutation_handler
@event_handler
class PolicyService(BaseService):

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['policy_id', 'name', 'permissions', 'domain_id'])
    def create(self, params):
        """Create Policy (local repo only)

        Args:
            params (dict): {
                'policy_id': 'str',
                'name': 'str',
                'permissions': 'list',
                'labels': 'list',
                'tags': 'dict',
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            policy_vo (object)
        """

        # Pre-condition Check
        _LOGGER.debug(f'[create] input param: {params} ')
        self._check_policy_id(params['policy_id'])
        self._check_project(params.get('project_id'), params['domain_id'])

        policy_mgr: LocalPolicyManager = self.locator.get_manager('LocalPolicyManager')

        # Only LOCAL repository can be created
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        params['repository'] = repo_mgr.get_local_repository()
        params['repository_id'] = params['repository'].repository_id

        return policy_mgr.create_policy(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['policy_id', 'domain_id'])
    def update(self, params):
        """Update Policy. (local repo only)

        Args:
            params (dict): {
                'policy_id': 'str',
                'name': 'str',
                'permissions': 'list',
                'labels': 'list',
                'tags': 'dict'
                'domain_id': 'str'
            }

        Returns:
            policy_vo (object)
        """

        policy_mgr: LocalPolicyManager = self.locator.get_manager('LocalPolicyManager')
        return policy_mgr.update_policy(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['policy_id', 'domain_id'])
    def delete(self, params):
        """Delete Policy (local repo only)

        Args:
            params (dict): {
                'policy_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            policy_vo (object)
        """
        policy_id = params['policy_id']
        domain_id = params['domain_id']

        policy_mgr: LocalPolicyManager = self.locator.get_manager('LocalPolicyManager')
        return policy_mgr.delete_policy(policy_id, domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['policy_id'])
    @change_only_key({'repository_info': 'repository'})
    def get(self, params):
        """ Get Policy (local & remote)

        Args:
            params (dict): {
                'policy_id': 'str',
                'repository_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            policy_vo (object)
        """
        policy_id = params['policy_id']
        domain_id = params.get('domain_id')
        repo_id = params.get('repository_id')
        only = params.get('only')

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repo_vos = repo_mgr.get_all_repositories(repo_id)

        for repo_vo in repo_vos:
            _LOGGER.debug(f'[get] find at name: {repo_vo.name} '
                          f'(repo_type: {repo_vo.repository_type})')
            policy_mgr = self._get_policy_manager_by_repo(repo_vo)
            try:
                policy_vo = policy_mgr.get_policy(policy_id, domain_id, only)
            except Exception as e:
                policy_vo = None

            if policy_vo:
                return policy_vo

        raise ERROR_NO_POLICY(policy_id=policy_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @change_only_key({'repository_info': 'repository'}, key_path='query.only')
    @append_query_filter(['repository_id', 'policy_id', 'name', 'project_id', 'domain_id'])
    @append_keyword_filter(['policy_id', 'name', 'labels'])
    def list(self, params):
        """ List policies (local or repo)

        Args:
            params (dict): {
                'repository_id': 'str',
                'policy_id': 'str',
                'name': 'str',
                'project_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            policy_vos (object)
            total_count
        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        query = params.get('query', {})

        if repository_id := params.get('repository_id'):
            repo_vo = repo_mgr.get_repository(repository_id)
            policy_mgr = self._get_policy_manager_by_repo(repo_vo)

            return policy_mgr.list_policies(query)
        else:
            repository_vos, total_count = repo_mgr.list_repositories({})

            all_policy_vos = []
            policy_total_count = 0
            for repository_vo in repository_vos:
                policy_mgr = self._get_policy_manager_by_repo(repository_vo)
                policy_vos, total_count = policy_mgr.list_policies(query)

                all_policy_vos += policy_vos
                policy_total_count += total_count

            return all_policy_vos, policy_total_count

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'repository_id'])
    @append_query_filter(['repository_id', 'domain_id'])
    @append_keyword_filter(['policy_id', 'name', 'labels'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        repository_id = params['repository_id']
        repo_vo = repo_mgr.get_repository(repository_id)

        policy_mgr = self._get_policy_manager_by_repo(repo_vo)
        query = params.get('query', {})
        return policy_mgr.stat_policies(query)

    def _get_policy_manager_by_repo(self, repo_vo):
        if repo_vo.repository_type == 'local':
            local_policy_mgr: LocalPolicyManager = self.locator.get_manager('LocalPolicyManager', repository=repo_vo)
            return local_policy_mgr
        else:
            remote_policy_mgr: RemotePolicyManager = self.locator.get_manager('RemotePolicyManager', repository=repo_vo)
            return remote_policy_mgr

    def _check_project(self, project_id, domain_id):
        if project_id:
            identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
            identity_mgr.get_project(project_id, domain_id)

    def _check_policy_id(self, policy_id):
        """ Check policy id
        format of policy id: alphabet lower case, number and - (underscore is not allowed)
        """
        _LOGGER.debug(f'[_check_policy_id] policy_id => {policy_id}')
        # check policy_id
        policy_id_len = len(policy_id)
        if policy_id_len > MAX_POLICY_ID_LENGTH:
            raise ERROR_INVALID_POLICY_ID_LENGTH(length=MAX_POLICY_ID_LENGTH, policy_id=policy_id)

        # Search policy_id format
        m = re.search('(?![a-z0-9\-]).*', policy_id)
        if m:
            if len(m.group()) > 1:
                raise ERROR_INVALID_POLICY_ID_FORMAT(policy_id=policy_id)
            return True
        raise ERROR_INVALID_POLICY_ID_FORMAT(policy_id=policy_id)
