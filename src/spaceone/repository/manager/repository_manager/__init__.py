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

    def get_repository(self, repository_id: str) -> dict:
        repos_info = self.get_repositories(repository_id=repository_id)
        if len(repos_info) == 0:
            raise ERROR_NOT_FOUND_REPOSITORY(repository_id=repository_id)
        return repos_info[0]

    @staticmethod
    def get_repositories(
        repository_id: str = None, repository_type: str = None
    ) -> list:
        repositories: list = config.get_global("REPOSITORIES", [])

        if repository_id:
            repositories = filter(
                lambda x: x["repository_id"] == repository_id, repositories
            )

        if repository_type:
            repositories = filter(
                lambda x: x["repository_type"] == repository_type, repositories
            )

        return list(repositories)

    def get_local_repository(self) -> dict:
        repos_info = self.get_repositories(repository_type="LOCAL")
        repo_count = len(repos_info)
        _LOGGER.debug(f"[get_managed_repository] local repo count: {repo_count}")
        if repo_count > 1:
            raise ERROR_ONLY_ONE_LOCAL_REPOSITORY_CAN_BE_REGISTERED(
                local_repository_count=repo_count
            )
        else:
            return repos_info[0]

    def get_managed_repository(self):
        repos_info = self.get_repositories(repository_type="MANGED")
        repo_count = len(repos_info)
        _LOGGER.debug(f"[get_managed_repository] managed repo count: {repo_count}")
        if repo_count > 1:
            raise ERROR_ONLY_ONE_MANAGED_REPOSITORY_CAN_BE_REGISTERED(
                managed_repository_count=repo_count
            )
        else:
            return None
