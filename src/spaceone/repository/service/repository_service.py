import logging

from spaceone.core.error import *
from spaceone.core.service import *
from spaceone.repository.manager import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class RepositoryService(BaseService):

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'repository_type'])
    def register(self, params):
        """
        Args:
            params:
                - name
                - repository_type: local | remote
                - endpoint
                - version
                - secret_id

        if repository_type == remote, do register remote repository
        """
        repo_type = params.get('repository_type')
        if repo_type == 'local':
            repo_mgr = self.locator.get_manager('LocalRepositoryManager')
        else:
            repo_mgr = self.locator.get_manager('RemoteRepositoryManager')

        return repo_mgr.register_repository(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['repository_id'])
    def update(self, params):
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        return repo_mgr.update_repository(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['repository_id'])
    def deregister(self, params):
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')

        return repo_mgr.delete_repository(params['repository_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['repository_id'])
    def get(self, params):
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        return repo_mgr.get_repository(params['repository_id'], params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @append_query_filter(['repository_id', 'name', 'repository_type'])
    @append_keyword_filter(['repository_id', 'name'])
    def list(self, params):
        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        query = params.get('query', {})
        return repo_mgr.list_repositories(query)
