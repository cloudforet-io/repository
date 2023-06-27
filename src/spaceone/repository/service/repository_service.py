import logging

from spaceone.core.service import *
from spaceone.repository.error import *
from spaceone.repository.manager import RepositoryManager, LocalRepositoryManager, ManagedRepositoryManager, \
    RemoteRepositoryManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class RepositoryService(BaseService):

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'repository_type'])
    def register(self, params):
        """ Register repository
        Args:
            params (dict):
                'name': 'str',
                'repository_type': 'local | remote | managed',
                'endpoint': 'str',
                'domain_id': 'str'

        Returns:
            repository_vo (object)
        """

        repo_type = params.get('repository_type')
        if repo_type == 'local':
            repo_mgr: LocalRepositoryManager = self.locator.get_manager('LocalRepositoryManager')
        elif repo_type == 'managed':
            repo_mgr: ManagedRepositoryManager = self.locator.get_manager('ManagedRepositoryManager')
        elif repo_type == 'remote':
            repo_mgr: RemoteRepositoryManager = self.locator.get_manager('RemoteRepositoryManager')
        else:
            raise ERROR_INVALID_REPOSITORY_TYPE()

        return repo_mgr.register_repository(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['repository_id'])
    def update(self, params):
        """ Update repository
        Args:
            params (dict):
                'repository_id': 'str',
                'name': 'str',
                'repository_type': 'local | remote | managed',
                'endpoint': 'str',
                'domain_id': 'str'

        Returns:
            repository_vo (object)
        """

        if params['repository_id'] == 'repo-managed':
            raise ERROR_NOT_UPDATE_MANAGED_REPOSITORY()

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        return repo_mgr.update_repository(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['repository_id'])
    def deregister(self, params):
        """ Deregister repository
        Args:
            params (dict):
                'repository_id': 'str',
                'domain_id': 'str'

        Returns:
            None
        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')

        return repo_mgr.delete_repository(params['repository_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['repository_id'])
    def get(self, params):
        """ Get repository
        Args:
            params (dict):
                'repository_id': 'str',
                'domain_id': 'str'

        Returns:
            repository_vo (object)
        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        return repo_mgr.get_repository(params['repository_id'], params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @append_query_filter(['repository_id', 'name', 'repository_type'])
    @append_keyword_filter(['repository_id', 'name'])
    def list(self, params):
        """ List repositories
        Args:
            params (dict):
                'repository_id': 'str',
                'name': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'

        Returns:
            results (list): 'list of repository_vo'
            total_count (int)
        """

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        query = params.get('query', {})
        return repo_mgr.list_repositories(query)
