import consul
import logging
import time

from spaceone.core import config
from spaceone.core.auth.jwt.jwt_util import JWTUtil
from spaceone.repository.manager.policy_manager import PolicyManager

__all__ = ['RemotePolicyManager']

_LOGGER = logging.getLogger(__name__)
_INTERVAL = 10


def _validate_token(token):
    if isinstance(token, dict):
        protocol = token['protocol']
        if protocol == 'consul':
            consul_instance = Consul(token['config'])
            value = False
            count = 0
            while value is False:
                uri = token['uri']
                value = consul_instance.patch_token(uri)
                _LOGGER.warn(f'[_validate_token] token: {value[:30]} uri: {uri}')
                if value:
                    break
                time.sleep(_INTERVAL)

            token = value

    return token


class RemotePolicyManager(PolicyManager):
    """
    self.repository (=repository_vo)
    Remote Policy make gRPC call to remote repository (like marketplace)
    If connector gets policy_info, this is gRPC message.
    """

    def get_policy(self, policy_id, domain_id, only=None):
        """
        Args:
            - policy_id
            - domain_id : my domain_id
        """
        conn = self._get_conn_from_repository(self.repository, domain_id)
        connector = self.locator.get_connector('RepositoryConnector', conn=conn)

        # policy_info, dict
        policy_info = connector.get_policy(policy_id, only)
        return self._get_updated_policy_info(policy_info)

    def list_policies(self, query, domain_id):
        conn = self._get_conn_from_repository(self.repository, domain_id)
        connector = self.locator.get_connector('RepositoryConnector', conn=conn)

        # Notice:
        # query should be JSON style query, not gRPC
        #

        response = connector.list_policies(query)
        _LOGGER.debug(f'[remote list_policy] count: {response.total_count}')

        for policy_info in response.results:
            # Warning:
            # This is side effect coding, since policy_vo is protobuf message
            self._get_updated_policy_info(policy_info)

        return response.results, response.total_count

    def stat_policies(self, query, domain_id):
        raise NotImplementedError('Remote repository is not supported.')

    def _get_conn_from_repository(self, repo, domain_id):
        """
        self.repository (repository_vo)

        Args:
            - repo: repository_vo (= self.repository)
            - domain_id: domain_id of credential
        """
        cred_id = repo.secret_id
        credentials = self._get_secret_data(cred_id, domain_id)
        conn = {
            'endpoint': repo.endpoint,
            'version': repo.version,
            'credential': {'token': credentials['token']}
        }
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

    ###############################
    # Credential/CredentialGroup
    ###############################
    def _get_secret_data(self, secret_id, domain_id):
        """ Return secret data
        """
        root_token = config.get_global('ROOT_TOKEN')
        root_token_info = config.get_global('ROOT_TOKEN_INFO')

        root_domain_id = domain_id
        if root_token != "":
            root_domain_id = self._get_domain_id_from_token(root_token)
            _LOGGER.debug(f'[_get_secret_data] root_domain_id: {root_domain_id} vs domain_id: {domain_id}')
        elif root_token_info:
            # Patch from Consul
            _LOGGER.debug(f'[_get_secret_data] Patch root_token from Consul')
            root_token = _validate_token(root_token_info)
            root_domain_id = self._get_domain_id_from_token(root_token)
        else:
            _LOGGER.warn(f'[_get_secret_data] root_token is not configured, may be your are root')
            root_token = self.transaction.get_meta('token')

        connector = self.locator.get_connector('SecretConnector', token=root_token, domain_id=root_domain_id)
        secret_data = connector.get_secret_data(secret_id, root_domain_id)
        return secret_data.data

    def _get_domain_id_from_token(self, token):
        decoded_token = JWTUtil.unverified_decode(token)
        return decoded_token['did']


class Consul:
    def __init__(self, config):
        """
        Args:
          - config: connection parameter

        Example:
            config = {
                    'host': 'consul.example.com',
                    'port': 8500
                }
        """
        self.config = self._validate_config(config)

    def _validate_config(self, config):
        """
        Parameter for Consul
        - host, port=8500, token=None, scheme=http, consistency=default, dc=None, verify=True, cert=None
        """
        options = ['host', 'port', 'token', 'scheme', 'consistency', 'dc', 'verify', 'cert']
        result = {}
        for item in options:
            value = config.get(item, None)
            if value:
              result[item] = value
        return result

    def patch_token(self, key):
        """
        Args:
            key: Query key (ex. /debug/supervisor/TOKEN)

        """
        try:
            conn = consul.Consul(**self.config)
            index, data = conn.kv.get(key)
            return data['Value'].decode('ascii')

        except Exception as e:
            return False
