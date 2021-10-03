import logging
from spaceone.repository.manager.plugin_manager import PluginManager
from spaceone.repository.connector.remote_repository_connector import RemoteRepositoryConnector

__all__ = ['RemotePluginManager']

_LOGGER = logging.getLogger(__name__)


class RemotePluginManager(PluginManager):
    """
    self.repository (=repository_vo)
    Remote Plugin make gRPC call to remote repository (like marketplace)
    If connector gets plugin_info, this is gRPC message.
    """

    def get_plugin(self, plugin_id, domain_id, only=None):
        conn = self._get_conn_from_repository()
        connector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)

        plugin_info = connector.get_plugin(plugin_id, only)
        return self._get_updated_plugin_info(plugin_info)

    def list_plugins(self, query):
        conn = self._get_conn_from_repository()
        connector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)

        response = connector.list_plugins(query, self.repository.repository_id)
        _LOGGER.debug(f'[remote list_plugin] count: {response.total_count}')

        for plugin_info in response.results:
            # Warning:
            # This is side effect coding, since plugin_vo is protobuf message
            self._get_updated_plugin_info(plugin_info)

        return response.results, response.total_count

    def stat_plugins(self, query):
        raise NotImplementedError('Remote repository is not supported.')

    def get_plugin_versions(self, plugin_id, domain_id):
        """ Get version of image

        version: tag list of docker image
        create RegistryConnector
        call get_tags()

        Returns:
            A list of docker tag
        """

        conn = self._get_conn_from_repository()
        connector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)

        versions = connector.get_plugin_version(plugin_id)
        _LOGGER.debug(f'[get_plugin_version] versions: {versions}')
        return versions

    def _get_conn_from_repository(self):
        conn = {'endpoint': self.repository.endpoint}
        return conn

    def _get_updated_plugin_info(self, plugin_info):
        """
        plugin_info is Protobuf Message
        We want to change our plugin_info (especially repository_info)

        Args:
            - plugin_info: protobuf message
        """
        # domain_id is remote repository's domain_id
        # change to local repository's domain_id  
        # There is no way to find domain_id
        # TODO: plugin_info.domain_id = self.repository.domain_id

        plugin_info.repository_info.name = self.repository.name
        plugin_info.repository_info.repository_type = self.repository.repository_type
        return plugin_info
