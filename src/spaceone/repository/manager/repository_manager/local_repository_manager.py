from spaceone.repository.manager.repository_manager import RepositoryManager


class LocalRepositoryManager(RepositoryManager):

    def register_repository(self, params):
        # Assume there is only one local repository

        return self.repo_model.create(params)
