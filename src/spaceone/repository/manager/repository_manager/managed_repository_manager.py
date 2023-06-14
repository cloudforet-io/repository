from spaceone.repository.manager.repository_manager import RepositoryManager


class ManagedRepositoryManager(RepositoryManager):

    def register_repository(self, params):
        # Assume there is only one local repository
        return self.repo_model.create(params)

    def register_default_repository(self, repo_name):
        # default
        params = {
            "name": repo_name,
            "repository_type": "managed"
            }
        return self.register_repository(params)
