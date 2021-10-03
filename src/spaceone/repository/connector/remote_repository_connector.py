import logging
from google.protobuf.json_format import MessageToDict

from spaceone.core.connector import BaseConnector
from spaceone.core import pygrpc
from spaceone.core.utils import parse_grpc_endpoint
from spaceone.repository.error import *

__all__ = ["RemoteRepositoryConnector"]

_LOGGER = logging.getLogger(__name__)


class RemoteRepositoryConnector(BaseConnector):
    client = None

    def __init__(self, transaction, config, **kwargs):
        super().__init__(transaction, config, **kwargs)

        """ Overwrite configuration

        Remote Repository has different authentication.
        So do not use your token at meta.
        Use another authentication algorithm like token

        Args:
            conn: dict (endpoint, version, ...)

        """

        e = parse_grpc_endpoint(self.conn['endpoint'])
        self.client = pygrpc.client(endpoint=e['endpoint'], ssl_enabled=e['ssl_enabled'])

        self.meta = []
        self.meta.append(('transaction_id', self.transaction.id))

        # if 'token' in self.conn:
        #     token = self.conn['token']
        #     self.meta.append(('token', self.conn['token']))

    def get_remote_repository(self):
        """ Repository.list
        Get Repository Information of Remote
        Return only 1 Repository
        """

        response = self.client.Repository.list({
            'repository_type': 'local'
        }, metadata=self.meta)

        return response.results[0]

    def get_policy(self, policy_id, only=None):
        params = {'policy_id': policy_id, 'only': only}
        _LOGGER.debug(f'[get_policy] params: {params}')
        return self.client.Policy.get(params, metadata=self.meta)

    def list_policies(self, query, repository_id):
        _LOGGER.debug(f'[list_policies] query: {query}')
        updated_query = self._remove_domain_id_from_query(query)
        params = {
            'repository_id': repository_id,
            'query': updated_query
        }
        _LOGGER.debug(f'[list_policies] params: {params}')
        return self.client.Policy.list(params, metadata=self.meta)

    def get_schema(self, name, only=None):
        params = {'name': name, 'only': only}
        _LOGGER.debug(f'[get_schema] params: {params}')
        return self.client.Schema.get(params, metadata=self.meta)

    def list_schemas(self, query, repository_id):
        _LOGGER.debug(f'[list_schemas] query: {query}')
        updated_query = self._remove_domain_id_from_query(query)
        params = {
            'repository_id': repository_id,
            'query': updated_query
        }
        _LOGGER.debug(f'[list_schemas] params: {params}')
        return self.client.Schema.list(params, metadata=self.meta)

    def get_plugin(self, plugin_id, only=None):
        params = {'plugin_id': plugin_id, 'only': only}
        _LOGGER.debug(f'[get_plugin] params: {params}')
        return self.client.Plugin.get(params, metadata=self.meta)

    def list_plugins(self, query, repository_id):
        _LOGGER.debug(f'[list_plugins] query: {query}')
        updated_query = self._remove_domain_id_from_query(query)
        params = {
            'repository_id': repository_id,
            'query': updated_query
        }
        _LOGGER.debug(f'[list_plugins] params: {params}')
        return self.client.Plugin.list(params, metadata=self.meta)

    def get_plugin_version(self, plugin_id):
        params = {'plugin_id': plugin_id}
        _LOGGER.debug(f'[get_plugin_version] params: {params}')
        message = self.client.Plugin.get_versions(params, metadata=self.meta)

        response = MessageToDict(message, preserving_proto_field_name=True)
        _LOGGER.debug(f'[get_plugin_version] response: {response}')

        return response.get('results', [])

    @staticmethod
    def _remove_domain_id_from_query(query):
        """
        query = {'page': {'start': 1.0, 'limit': 2.0}}

        Remove domain_id at filter
        Update page to int value (may be float)
        """

        new_query = query.copy()
        change_query_filter = []

        for condition in new_query.get('filter', []):
            key = condition.get('k', condition.get('key'))
            if key != 'domain_id':
                change_query_filter.append(condition)

        new_query['filter'] = change_query_filter
        return new_query
