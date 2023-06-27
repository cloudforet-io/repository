import logging
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.repository.model.repository_model import Repository
from spaceone.repository.manager.schema_manager import SchemaManager

__all__ = ['RemoteSchemaManager']

_LOGGER = logging.getLogger(__name__)


class RemoteSchemaManager(SchemaManager):

    def get_schema(self, repo_vo: Repository, schema_name, domain_id, only=None):
        endpoint = repo_vo.endpoint
        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)
        schema_info = remote_repo_conn.dispatch('Schema.get', {
            'name': schema_name,
            'only': only
        })

        return self.change_response(schema_info, repo_vo, domain_id)

    def list_schemas(self, repo_vo: Repository, query: dict, params: dict):
        domain_id = params.get('domain_id')
        endpoint = repo_vo.endpoint
        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)

        response = remote_repo_conn.dispatch('Schema.list', {
            'query': query,
            'repository_id': repo_vo.repository_id
        })

        schemas_info = response.get('results', [])
        total_count = response.get('total_count', 0)
        results = []
        for schema_info in schemas_info:
            results.append(self.change_response(schema_info, repo_vo, domain_id))

        return results, total_count
