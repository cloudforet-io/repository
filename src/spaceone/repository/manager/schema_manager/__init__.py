import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager

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
    def get_schema(self, schema_id, domain_id):
        pass

    @abstractmethod
    def list_schemas(self, query, domain_id):
        pass

    @abstractmethod
    def stat_schemas(self, query, domain_id):
        pass
