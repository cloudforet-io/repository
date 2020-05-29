import consul
import logging
import time

from spaceone.core import config
from spaceone.core.auth.jwt.jwt_util import JWTUtil

from spaceone.repository.connector.repository_connector import RepositoryConnector
from spaceone.repository.manager.repository_manager import RepositoryManager

_INTERVAL = 10
_LOGGER = logging.getLogger(__name__)


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

    _LOGGER.debug(f'[_validate_token] token: {list(token)}')
    return token


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

        Connect to Remote Repository via secret_id
        Get repository_id of remote.
        use remote's repository_id as my repository_id
        """
        domain_id = self._get_domain_id_from_token(self.transaction.get_meta('token'))
        remote_token = self._get_secret(params.get('secret_id', None), domain_id)

        conn = {
            'endpoint': params.get('endpoint', None),
            'version': params.get('version', None),
            'credential': {'token': remote_token['token']}
        }

        connector: RepositoryConnector = self.locator.get_connector('RepositoryConnector', conn=conn)
        repo_info = connector.get_local_repository()
        # Overwrite repository_id to Remote one
        params['repository_id'] = repo_info.repository_id

        # TODO: connect remote repository, then check
        return self.repo_model.create(params)

    ###############################
    # Secret/SecretGroup
    ###############################
    def _get_secret(self, secret_id, domain_id):
        """ Return secret data

        This call must be root domain.
        DO NOT check ROOT_TOKEN

        """
        root_token = config.get_global('ROOT_TOKEN')
        root_token_info = config.get_global('ROOT_TOKEN_INFO')

        root_domain_id = domain_id
        if root_token != "":
            root_domain_id = self._get_domain_id_from_token(root_token)
            _LOGGER.debug(f'[_get_secret] root_domain_id: {root_domain_id} vs domain_id: {domain_id}')
        elif root_token_info:
            # Patch from Consul
            _LOGGER.debug(f'[_get_secret] Patch root_token from Consul')
            root_token = _validate_token(root_token_info)
            root_domain_id = self._get_domain_id_from_token(root_token)
        else:
            _LOGGER.warn(f'[_get_secret] root_token is not configured, may be your are root')
            root_token = self.transaction.get_meta('token')


        connector = self.locator.get_connector('SecretConnector', token=root_token, domain_id=root_domain_id)
        secret_data = connector.get_secret_data(secret_id, domain_id)
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
