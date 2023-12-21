import logging
from abc import abstractmethod

from typing import List, Tuple, Union
from spaceone.core import config
from spaceone.core.manager import BaseManager

from spaceone.repository.error.repository import *

_LOGGER = logging.getLogger(__name__)


class RepositoryManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def register_repository(self, params):
        pass

    def get_repository(self, repository_id: str):
        repo_info, _ = self.list_repositories(repository_id=repository_id)
        return repo_info[0]

    @staticmethod
    def list_repositories(
        repository_id: str = None, repository_type: str = None
    ) -> Tuple[list, int]:
        repositories: list = config.get_global("REPOSITORIES", [])

        if repository_id:
            repositories: list = [
                repository
                for repository in repositories
                if repository.get("repository_id") == repository_id
            ]

        if repository_type:
            repositories: list = [
                repository
                for repository in repositories
                if repository.get("repository_type") == repository_type
            ]

        return repositories, len(repositories)

    def get_all_repositories(self, repository_id: str = None) -> Union[List, None]:
        repos_info, total_count = self.list_repositories(repository_id=repository_id)
        _LOGGER.debug(f"[get_all_repositories] Number of repositories: {total_count}")

        return repos_info

    def get_local_repository(self) -> dict:
        repos_info, local_repo_count = self.list_repositories(repository_type="LOCAL")
        _LOGGER.debug(f"[get_local_repository] local_repo_count: {local_repo_count}")
        if local_repo_count > 1:
            raise ERROR_ONLY_ONE_LOCAL_REPOSITORY_CAN_BE_REGISTERED(
                local_repository_count=local_repo_count
            )
        else:
            return repos_info[0]

    def get_managed_repository(self):
        repos_info, repo_count = self.list_repositories(repository_type="MANGED")
        _LOGGER.debug(f"[get_managed_repository] managed_repo_count: {repo_count}")
        if repo_count > 1:
            raise ERROR_ONLY_ONE_MANAGED_REPOSITORY_CAN_BE_REGISTERED(
                managed_repository_count=repo_count
            )
        else:
            return None
