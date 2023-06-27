import logging

from spaceone.repository.model.schema_model import Schema
from spaceone.repository.model.repository_model import Repository
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

        schema_info = schema_vo.to_dict()
        return self.change_response(schema_info, schema_vo.repository)

    def update_schema(self, params):
        schema_vo = self.schema_model.get(name=params['name'], domain_id=params['domain_id'])
        return self.update_schema_by_vo(params, schema_vo)

    def update_schema_by_vo(self, params, schema_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Schema Data : {old_data["name"]}')
            schema_vo.update(old_data)

        self.transaction.add_rollback(_rollback, schema_vo.to_dict())
        schema_vo = schema_vo.update(params)

        schema_info = schema_vo.to_dict()
        return self.change_response(schema_info, schema_vo.repository)

    def delete_schema(self, schema_name, domain_id):
        schema_vo = self.schema_model.get(name=schema_name, domain_id=domain_id)
        schema_vo.delete()

    def get_schema(self, repo_vo: Repository, schema_name, domain_id, only=None):
        schema_vo = self.schema_model.get(name=schema_name, domain_id=domain_id, only=only)

        schema_info = schema_vo.to_dict()
        return self.change_response(schema_info, schema_vo.repository)

    def list_schemas(self, repo_vo: Repository, query: dict, params: dict):
        domain_id = params.get('domain_id')
        keyword = query.get('keyword')
        query_filter = query.get('filter', [])
        query_filter_or = query.get('filter_or', [])
        query['filter'] = self._append_domain_filter(query_filter, domain_id)
        query['filter_or'] = self._append_keyword_filter(query_filter_or, keyword)

        schema_vos, total_count = self.schema_model.query(**query)
        results = []
        for schema_vo in schema_vos:
            schema_info = schema_vo.to_dict()
            results.append(self.change_response(schema_info, schema_vo.repository))

        return results, total_count

    def stat_schemas(self, query):
        return self.schema_model.stat(**query)

    @staticmethod
    def _append_domain_filter(query_filter, domain_id=None):
        if domain_id:
            query_filter.append({
                'k': 'domain_id',
                'v': domain_id,
                'o': 'eq'
            })

        return query_filter

    @staticmethod
    def _append_keyword_filter(query_filter_or, keyword):
        if keyword:
            query_filter_or.append({
                'k': 'name',
                'v': keyword,
                'o': 'contain'
            })

        return query_filter_or
