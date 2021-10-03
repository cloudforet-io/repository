import logging
from spaceone.repository.manager.policy_manager import PolicyManager
from spaceone.repository.connector.remote_repository_connector import RemoteRepositoryConnector

__all__ = ['RemotePolicyManager']

_LOGGER = logging.getLogger(__name__)


class RemotePolicyManager(PolicyManager):
    """
    self.repository (=repository_vo)
    Remote Policy make gRPC call to remote repository (like marketplace)
    If connector gets policy_info, this is gRPC message.
    """

    def get_policy(self, policy_id, domain_id, only=None):
        conn = self._get_conn_from_repository()
        connector: RemoteRepositoryConnector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)

        policy_info = connector.get_policy(policy_id, only)
        return self._get_updated_policy_info(policy_info)

    def list_policies(self, query):
        conn = self._get_conn_from_repository()
        connector: RemoteRepositoryConnector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)

        response = connector.list_policies(query, self.repository.repository_id)
        _LOGGER.debug(f'[remote list_policy] count: {response.total_count}')

        for policy_info in response.results:
            # Warning:
            # This is side effect coding, since policy_vo is protobuf message
            self._get_updated_policy_info(policy_info)

        return response.results, response.total_count

    def stat_policies(self, query):
        raise NotImplementedError('Remote repository is not supported.')

    def _get_conn_from_repository(self):
        conn = {'endpoint': self.repository.endpoint}
        return conn

    def _get_updated_policy_info(self, policy_info):
        """
        policy_info is Protobuf Message
        We want to change our policy_info (especially repository_info)

        Args:
            - policy_info: protobuf message
        """
        # domain_id is remote repository's domain_id
        # change to local repository's domain_id  
        # There is no way to find domain_id
        # TODO: policy_info.domain_id = self.repository.domain_id

        policy_info.repository_info.name = self.repository.name
        policy_info.repository_info.repository_type = self.repository.repository_type
        return policy_info
