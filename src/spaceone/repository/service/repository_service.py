import logging

from spaceone.core.service import *
from spaceone.repository.manager import (
    RepositoryManager,
)

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class RepositoryService(BaseService):
    resource = "Repository"

    @transaction(
        permission="repository:Repository.read",
        role_types=[
            "SYSTEM_ADMIN",
            "DOMAIN_ADMIN",
            "WORKSPACE_OWNER",
            "WORKSPACE_MEMBER",
        ],
    )
    def list(self, params):
        """List repositories
        Args:
            params (dict):
                'repository_id': 'str',
                'repository_type': 'str'

        Returns:
            results (list): 'list of repository_vo'
            total_count (int)
        """
        repository_id: str = params.get("repository_id")
        repository_type: str = params.get("repository_type")
        repo_mgr: RepositoryManager = self.locator.get_manager("RepositoryManager")

        repositories_info = repo_mgr.get_repositories(repository_id, repository_type)
        repositories_info.reverse()

        return repositories_info
