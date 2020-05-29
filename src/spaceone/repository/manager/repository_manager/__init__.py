import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager
from spaceone.repository.model.repository_model import Repository

_LOGGER = logging.getLogger(__name__)


class RepositoryManager(BaseManager):
    def __init__(self, transaction, **kwargs):
        super().__init__(transaction, **kwargs)
        self.repo_model : Repository = self.locator.get_model('Repository')

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

    def list_repositories(self, query):
        return self.repo_model.query(**query)

    def stat_repositories(self, query):
        return self.repo_model.stat(**query)

    def get_repository_by_name(self, name='local'):
        return self.repo_model.get(name=name)

    def get_repository_by_type(self, repository_type):
        query = {'filter': [{'k':'repository_type', 'v': repository_type, 'o':'eq'}]}
        return self.list_repositories(query)

    def get_local_repository(self):
        result, count = self.get_repository_by_type('local')
        _LOGGER.debug(f'[get_local_repository] local_repo_count: {count}')
        return result[0]
