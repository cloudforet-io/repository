from spaceone.core import utils

from spaceone.repository.error import *
from spaceone.repository.manager.repository_manager import RepositoryManager


class LocalRepositoryManager(RepositoryManager):
    def register_repository(self, params):
        # Assume there is only one local repository
        local_repos_info = self.get_local_repository()
        if local_repos_info is not None:
            raise ERROR_LOCAL_REPOSITORY_ALREADY_EXIST()

        params["repository_id"] = utils.generate_id("repo")
        params["order"] = 3

        return self.repo_model.create(params)
