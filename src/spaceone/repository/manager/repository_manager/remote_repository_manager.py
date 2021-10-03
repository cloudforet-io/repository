import logging

from spaceone.core.error import *
from spaceone.core.auth.jwt.jwt_util import JWTUtil

from spaceone.repository.connector.remote_repository_connector import RemoteRepositoryConnector
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)


class RemoteRepositoryManager(RepositoryManager):

    def register_repository(self, params):
        """
        Args:
            params:
                - name
                - repository_type: remote
                - endpoint
                - version
                - secret_id
                - domain_id

        Connect to Remote Repository via secret_id
        Get repository_id of remote.
        use remote's repository_id as my repository_id
        """

        endpoint = params.get('endpoint')
        secret_id = params.get('secret_id')

        if endpoint is None:
            raise ERROR_REQUIRED_PARAMETER(key='endpoint')

        conn = {'endpoint': endpoint}

        # if secret_id:
        #     token = self.transaction.get_meta('token')
        #     if token is None:
        #         raise ERROR_AUTHENTICATE_FAILURE(message='Empty token provided.')
        #
        #     domain_id = self._get_domain_id_from_token(token)
        #     remote_token = self._get_secret(secret_id, domain_id)
        #     conn['token'] = remote_token['token']

        connector: RemoteRepositoryConnector = self.locator.get_connector('RemoteRepositoryConnector', conn=conn)
        repo_info = connector.get_remote_repository()
        # Overwrite repository_id to Remote one
        params['repository_id'] = repo_info.repository_id

        return self.repo_model.create(params)

    def _get_domain_id_from_token(self, token):
        decoded_token = JWTUtil.unverified_decode(token)
        return decoded_token['did']
