import boto3
import base64
import logging
from docker_registry_client import DockerRegistryClient

from spaceone.core.connector import BaseConnector
from spaceone.repository.error import *

__all__ = ["RegistryConnector"]

_LOGGER = logging.getLogger(__name__)


class RegistryConnector(BaseConnector):
    def __init__(self, transaction, config):
        super().__init__(transaction, config)

    def get_tags(self, image):
        params = {}
        for (k, v) in self.config.items():
            if v == '' or v is None:
                continue
            # FOR AWS ECR User
            if k == 'username' and v == 'AWS':
                # get password
                region_name = self._get_aws_region_from_host(self.config['host'])
                password = self._get_aws_ecr_token(region_name)
                if password:
                    params.update({'password': password})
            params.update({k: v})

        try:
            client = DockerRegistryClient(**params)
            r = client.repository(image)
            tags = r.tags()
            # return sorted list
            return tags
        except Exception as e:
            # Hard to determine backend problems
            _LOGGER.error(f"Error to get container tags: {e}")
            raise ERROR_REPOSITORY_BACKEND(host=params['host'])

    def _get_aws_region_from_host(self, host):
        # host = https://<account_id>.dkr.ecr.ap-northeast-2.amazonaws.com
        item = host.split('.')
        return item[3]

    def _get_aws_ecr_token(self, region_name):
        try:
            sess = boto3.Session()
            resp = sess.client('ecr', region_name=region_name).get_authorization_token()
            token = resp['authorizationData'][0]['authorizationToken']
            token = base64.b64decode(token).decode()
            username, password = token.split(':')
            return password
        except Exception as e:
            _LOGGER.error(f'[_get_aws_ecr_token] {e}')
            raise ERROR_AWS_ECR_TOKEN()

if __name__ == "__main__":
    from spaceone.core.transaction import Transaction
    tnx = Transaction()
    config = {'host': 'https://<account_id>.dkr.ecr.ap-northeast-2.amazonaws.com',
              'verify_ssl': False,
              'username': 'AWS',
              'api_version': 2}

    r = RegistryConnector(tnx, config)
    a = r.get_tags('spaceone/server-mockup')
    print(a)
