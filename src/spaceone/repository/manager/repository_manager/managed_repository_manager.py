from spaceone.repository.error import *
from spaceone.repository.manager.repository_manager import RepositoryManager


class ManagedRepositoryManager(RepositoryManager):

    def register_repository(self, params):
        # Assume there is only one local repository
        managed_repo_vo = self.get_managed_repository()
        if managed_repo_vo is not None:
            raise ERROR_MANAGED_REPOSITORY_ALREADY_EXIST()

        params['repository_id'] = 'repo-managed'
        params['order'] = 1
        return self.repo_model.create(params)
