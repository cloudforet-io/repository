import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager
from spaceone.repository.model.repository_model import Repository

__all__ = ['SchemaManager']

_LOGGER = logging.getLogger(__name__)


class SchemaManager(BaseManager):

    def create_schema(self, params):
        pass

    def update_schema(self, params):
        pass

    def delete_schema(self, schema_id, domain_id):
        pass

    @abstractmethod
    def get_schema(self, repo_vo: Repository, schema_name, domain_id, only=None):
        pass

    @abstractmethod
    def list_schemas(self, repo_vo: Repository, query: dict, params: dict):
        pass

    def stat_schemas(self, query):
        pass

    @staticmethod
    def change_response(info, repo_vo: Repository = None, domain_id: str = None):
        if repo_vo:
            info['repository_info'] = {
                'repository_id': repo_vo.repository_id,
                'name': repo_vo.name,
                'repository_type': repo_vo.repository_type,
            }

        if domain_id:
            info['domain_id'] = domain_id

        return info
