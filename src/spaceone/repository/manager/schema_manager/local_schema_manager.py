import logging

from spaceone.core import config
from spaceone.core.error import *
from spaceone.repository.model import *
from spaceone.repository.manager.schema_manager import SchemaManager

__all__ = ['LocalSchemaManager']

_LOGGER = logging.getLogger(__name__)


class LocalSchemaManager(SchemaManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_model: Schema = self.locator.get_model("Schema")

    def register_schema(self, params):
        def _rollback(schema_vo):
            schema_vo.delete()

        schema_vo = self.schema_model.create(params)
        self.transaction.add_rollback(_rollback, schema_vo)

        return schema_vo

    def update_schema(self, params):
        schema_vo = self.get_schema(params['name'], params['domain_id'])
        return self.update_schema_by_vo(params, schema_vo)

    def update_schema_by_vo(self, params, schema_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Schema Data : {old_data["name"]}')
            schema_vo.update(old_data)

        self.transaction.add_rollback(_rollback, schema_vo.to_dict())
        return schema_vo.update(params)

    def delete_schema(self, schema_name, domain_id):
        schema_vo = self.schema_model.get(domain_id=domain_id, name=schema_name)
        schema_vo.delete()

    def get_schema(self, schema_name, domain_id, only=None):
        schema_vo = self.schema_model.get(domain_id=domain_id, name=schema_name, only=only)
        return schema_vo

    def list_schemas(self, query, domain_id):
        return self.schema_model.query(**query)

    def stat_schemas(self, query, domain_id):
        return self.schema_model.stat(**query)
