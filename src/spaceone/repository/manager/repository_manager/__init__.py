import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager
from spaceone.repository.model.repository_model import Repository

_LOGGER = logging.getLogger(__name__)


class RepositoryManager(BaseManager):
    def __init__(self, transaction, **kwargs):
        super().__init__(transaction, **kwargs)
        self.repo_model: Repository = self.locator.get_model('Repository')

    @abstractmethod
    def register_repository(self, params):
        pass

    def delete_repository(self, repository_id):
        repo_vo = self.repo_model.get(repository_id=repository_id)
        repo_vo.delete()

    def update_repository(self, params):
        def _rollback(old_data):
            repo_vo.update(old_data)

        repo_vo = self.repo_model.get(repository_id=params['repository_id'])
        self.transaction.add_rollback(_rollback, repo_vo.to_dict())
        
        repo_vo.update(params)
        return repo_vo

    def get_repository(self, repository_id, only=None):
        return self.repo_model.get(repository_id=repository_id, only=only)

    def filter_repositories(self, **conditions):
        return self.repo_model.filter(**conditions)

    def list_repositories(self, query):
        return self.repo_model.query(**query)

    def stat_repositories(self, query):
        return self.repo_model.stat(**query)

    def get_all_repositories(self, repository_id=None):
        query = {
            'sort': {
                'key': 'repository_type'
            },
            'filter': []
        }

        if repository_id:
            query['filter'].append({'k': 'repository_id', 'v': repository_id, 'o': 'eq'})

        repo_vos, total_count = self.list_repositories(query)
        _LOGGER.debug(f'[list_repositories_by_id] Number of repositories: {total_count}')

        return repo_vos

    def get_local_repository(self):
        repo_vos = self.filter_repositories(repository_type='local')
        local_repo_count = repo_vos.count()
        _LOGGER.debug(f'[get_local_repository] local_repo_count: {local_repo_count}')
        if local_repo_count > 0:
            return repo_vos[0]
        else:
            return None


