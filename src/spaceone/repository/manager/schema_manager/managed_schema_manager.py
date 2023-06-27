import logging
import os
import copy
import pandas as pd
import re

from spaceone.core import utils
from spaceone.repository.error import *
from spaceone.repository.manager.schema_manager import SchemaManager
from spaceone.repository.model.repository_model import Repository


__all__ = ['ManagedSchemaManager']

_LOGGER = logging.getLogger(__name__)
_BASE_DIR = os.path.join(os.path.dirname(__file__), '../../managed_resource/schema/')
_MANAGED_SCHEMAS = []

for filename in os.listdir(_BASE_DIR):
    if filename.endswith('.yaml'):
        file_path = os.path.join(_BASE_DIR, filename)
        schema_info = utils.load_yaml_from_file(file_path)
        _MANAGED_SCHEMAS.append(schema_info)


class ManagedSchemaManager(SchemaManager):

    def __init__(self):
        super().__init__()
        self.managed_schema_df = self._load_managed_schemas()

    def get_schema(self, repo_vo: Repository, schema_name, domain_id, only=None):
        managed_schema_df = self._filter_managed_schemas(schema_name)

        if len(managed_schema_df) == 0:
            raise ERROR_NOT_FOUND(key='name', value=schema_name)

        managed_schemas_info = managed_schema_df.to_dict('records')

        return self.change_response(managed_schemas_info[0], repo_vo, domain_id)

    def list_schemas(self, repo_vo: Repository, query: dict, params: dict):
        schema_name = params.get('name')
        service_type = params.get('service_type')
        domain_id = params.get('domain_id')
        sort = query.get('sort', {})
        page = query.get('page', {})
        keyword = query.get('keyword')

        managed_schema_df = self._filter_managed_schemas(schema_name, service_type, keyword)
        managed_schema_df = self._sort_managed_schemas(managed_schema_df, sort)

        total_count = len(managed_schema_df)
        managed_schema_df = self._page_managed_schemas(managed_schema_df, page)

        results = []
        for managed_schema_info in managed_schema_df.to_dict('records'):
            results.append(self.change_response(managed_schema_info, repo_vo, domain_id))

        return results, total_count

    @staticmethod
    def _load_managed_schemas():
        return pd.DataFrame(copy.deepcopy(_MANAGED_SCHEMAS))

    def _filter_managed_schemas(self, schema_name=None, service_type=None, keyword=None):
        managed_schema_df = copy.deepcopy(self.managed_schema_df)

        if schema_name:
            managed_schema_df = managed_schema_df[managed_schema_df['name'] == schema_name]

        if service_type:
            managed_schema_df = managed_schema_df[managed_schema_df['service_type'] == service_type]

        if keyword:
            managed_schema_df = managed_schema_df[
                managed_schema_df['name'].str.contains(keyword, flags=re.IGNORECASE)]

        return managed_schema_df

    @staticmethod
    def _sort_managed_schemas(managed_schema_df: pd.DataFrame, sort: dict):
        if sort_key := sort.get('key'):
            desc = sort.get('desc', False)
            try:
                return managed_schema_df.sort_values(by=sort_key, ascending=not desc)
            except Exception as e:
                raise ERROR_SORT_KEY(sort_key=sort_key)
        else:
            return managed_schema_df

    @staticmethod
    def _page_managed_schemas(managed_schema_df: pd.DataFrame, page: dict):
        if limit := page.get('limit'):
            start = page.get('start', 1) - 1
            return managed_schema_df[start:start + limit]
        else:
            return managed_schema_df
