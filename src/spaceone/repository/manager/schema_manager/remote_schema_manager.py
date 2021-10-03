import logging
from spaceone.repository.manager.schema_manager import SchemaManager
from spaceone.repository.connector.remote_repository_connector import RemoteRepositoryConnector

__all__ = ['RemoteSchemaManager']

_LOGGER = logging.getLogger(__name__)


class RemoteSchemaManager(SchemaManager):
    """
    self.repository (=repository_vo)
    Remote Schema make gRPC call to remote repository (like marketplace)
    If connector gets schema_info, this is gRPC message.
    """

    def get_schema(self, schema_id, domain_id, only=None):
        conn = self._get_conn_from_repository()
        connector: RemoteRepositoryConnector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)

        schema_info = connector.get_schema(schema_id, only)
        return self._get_updated_schema_info(schema_info)        

    def list_schemas(self, query):
        conn = self._get_conn_from_repository()
        connector: RemoteRepositoryConnector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)

        response = connector.list_schemas(query, self.repository.repository_id)
        _LOGGER.debug(f'[remote list_schema] count: {response.total_count}')

        for schema_info in response.results:
            # Warning:
            # This is side effect coding, since schema_vo is protobuf message
            self._get_updated_schema_info(schema_info)

        return response.results, response.total_count

    def stat_schemas(self, query):
        raise NotImplementedError('Remote repository is not supported.')

    def _get_conn_from_repository(self):
        conn = {'endpoint': self.repository.endpoint}
        return conn

    def _get_updated_schema_info(self, schema_info):
        """
        schema_info is Protobuf Message
        We want to change our schema_info (especially repository_info)

        Args:
            - schema_info: protobuf message
        """
        # domain_id is remote repository's domain_id
        # change to local repository's domain_id  
        # There is no way to find domain_id
        # TODO: schema_info.domain_id = self.repository.domain_id

        schema_info.repository_info.name = self.repository.name
        schema_info.repository_info.repository_type = self.repository.repository_type
        return schema_info
