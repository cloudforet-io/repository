import copy
import logging

from spaceone.core import config
from spaceone.core.error import *
from spaceone.repository.model import *
from spaceone.repository.manager.schema_manager import SchemaManager

from spaceone.repository.manager.identity_manager import IdentityManager

__all__ = ['ManagedSchemaManager']

_LOGGER = logging.getLogger(__name__)


class ManagedSchemaManager(SchemaManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_model: Schema = self.locator.get_model("Schema")
        identity_mgr = self.locator.get_manager('IdentityManager')
        self.domain_id = identity_mgr.get_root_domain_id()

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
        schema_vo = self.schema_model.get(name=schema_name, domain_id=domain_id)
        schema_vo.delete()

    def get_schema(self, schema_name, domain_id, only=None):
        schema_vo = self.schema_model.get(name=schema_name, domain_id=self.domain_id, only=only)

        return schema_vo

    def list_schemas(self, query):
        new_query = self._change_domain_id(query)
        return self.schema_model.query(**new_query)

    def stat_schemas(self, query):
        return self.schema_model.stat(**query)

    def _change_domain_id(self, query):
        new_query = copy.deepcopy(query)
        q_list = new_query.get('filter', [])
        new_list = []
        appended = False
        for item in q_list:
            if 'k' in item:
                if item['k'] == 'domain_id':
                    new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
                    appended = True
                else:
                    new_list.append(item)
            if 'key' in item:
                if item['key'] == 'domain_id':
                    new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
                    appended = True
                else:
                    new_list.append(item)
 
        if appended == False:
            new_list.append({'k': 'domain_id', 'v': self.domain_id, 'o': 'eq'})
        new_query['filter'] = new_list
        return new_query
