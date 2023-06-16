import logging

from spaceone.core import cache
from spaceone.core import config
from spaceone.core.error import *
from spaceone.core.service import *
from spaceone.repository.manager import *
from spaceone.repository.service.plugin_service import PluginService
from spaceone.repository.service.policy_service import PolicyService
from spaceone.repository.service.schema_service import SchemaService

from spaceone.repository.manager.identity_manager import IdentityManager

_LOGGER = logging.getLogger(__name__)


MANAGED_REPO_NAME = "managed-local"

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
                - repository_type: local | remote | config
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
        # check default
        managed_repo = config.get_global("ENABLE_MANAGED_REPOSITORY", False)
        if managed_repo:
            self._create_managed_repository()

        repo_mgr: RepositoryManager = self.locator.get_manager('RepositoryManager')
        query = params.get('query', {})
        return repo_mgr.list_repositories(query)

    # TEST
    #@cache.cacheable(key='repository:managed:init', expire=300)
    def _create_managed_repository(self):
        identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
        domain_id = identity_mgr.get_root_domain_id()
        repo_mgr: RepositoryManager = self.locator.get_manager("ManagedRepositoryManager")
        query = {
                'filter': [{'k': 'repository_type', 'v': 'managed', 'o': 'eq'}]
                }
        repo_vos, total_count = repo_mgr.list_repositories(query)
        # total_count is 0 or 1
        if total_count == 1:
            return False
        # Not Found
        # Init Managed Repository
        repo_mgr.register_default_repository(MANAGED_REPO_NAME)

        # Init Plugin
        _LOGGER.debug("Create Managed Plugins")
        plugin_svc: PluginService = self.locator.get_service("PluginService")
        plugin_svc.create_managed_plugins(domain_id)

        # Init Policy
        _LOGGER.debug("Create Managed Policy")
        policy_svc: PolicyService = self.locator.get_service("PolicyService")
        policy_svc.create_managed_policies(domain_id)

        # Init Schema
        _LOGGER.debug("Create Managed Schema")
        schema_svc: SchemaService = self.locator.get_service("SchemaService")
        schema_svc.create_managed_schemas(domain_id)
       	return True
