import abc
import requests
import logging
import boto3

from spaceone.core.connector import BaseConnector
from spaceone.repository.error import *

__all__ = ["DockerHubConnector", "AWSPublicECRConnector"]

_LOGGER = logging.getLogger(__name__)


class RegistryConnector(BaseConnector):

    @abc.abstractmethod
    def get_tags(self, registry_url, image):
        pass


class DockerHubConnector(RegistryConnector):

    _DEFAULT_PAGE_SIZE = 1024

    def get_tags(self, registry_url, image):
        url = f'https://{registry_url}/v2/repositories/{image}/tags?page_size={self._DEFAULT_PAGE_SIZE}'

        response = requests.get(url)

        if response.status_code == 200:
            image_tags = []
            results = response.json().get('results', [])
            for tag in results:
                image_tags.append(tag['name'])

            return image_tags

        else:
            raise ERROR_NO_IMAGE_IN_REGISTRY(image=image, registry_url=registry_url)


class AWSPublicECRConnector(RegistryConnector):

    def __init__(self, transaction, config):
        super().__init__(transaction, config)

        aws_access_key_id = self.config.get('aws_access_key_id')
        aws_secret_access_key = self.config.get('aws_secret_access_key')
        region_name = self.config.get('region_name')

        if not all([aws_access_key_id, aws_secret_access_key, region_name]):
            raise ERROR_CONNECTOR_CONFIGURATION(connector='AWSECRConnector')

        self.client = boto3.client('ecr', aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    def get_tags(self, registry_url, image):
        print(registry_url, image)
        pass


if __name__ == '__main__':
    docker_hub_conn = DockerHubConnector()
    tags = docker_hub_conn.get_tags('registry.hub.docker.com', 'pyengine/plugin-keycloak-identity-auth')
    print(tags)

    # from spaceone.core.transaction import Transaction
    # aws_ecr_conn = AWSECRConnector(Transaction(), {
    #     'aws_access_key_id': 'AKIATYAD7BLQJVVYSGMS',
    #     'aws_secret_access_key': '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',
    #     'region_name': 'ap-northeast-2'
    # })

#
# class RegistryConnector(BaseConnector):
#     def __init__(self, transaction, config):
#         super().__init__(transaction, config)
#
#     def get_tags(self, image):
#         params = {}
#         for (k, v) in self.config.items():
#             if v == '' or v is None:
#                 continue
#             # FOR AWS ECR User
#             if k == 'username' and v == 'AWS':
#                 # get password
#                 region_name = self._get_aws_region_from_host(self.config['host'])
#                 password = self._get_aws_ecr_token(region_name)
#                 if password:
#                     params.update({'password': password})
#             params.update({k: v})
#
#         try:
#             client = DockerRegistryClient(**params)
#             r = client.repository(image)
#             tags = r.tags()
#             # return sorted list
#             return tags
#         except Exception as e:
#             # Hard to determine backend problems
#             _LOGGER.error(f"Error to get container tags: {e}")
#             raise ERROR_REPOSITORY_BACKEND(host=params['host'])
#
#     def _get_aws_region_from_host(self, host):
#         # host = https://<account_id>.dkr.ecr.ap-northeast-2.amazonaws.com
#         item = host.split('.')
#         return item[3]
#
#     def _get_aws_ecr_token(self, region_name):
#         try:
#             sess = boto3.Session()
#             resp = sess.client('ecr', region_name=region_name).get_authorization_token()
#             token = resp['authorizationData'][0]['authorizationToken']
#             token = base64.b64decode(token).decode()
#             username, password = token.split(':')
#             return password
#         except Exception as e:
#             _LOGGER.error(f'[_get_aws_ecr_token] {e}')
#             raise ERROR_AWS_ECR_TOKEN()
#
# if __name__ == "__main__":
#     from spaceone.core.transaction import Transaction
#     tnx = Transaction()
#     config = {'host': 'https://<account_id>.dkr.ecr.ap-northeast-2.amazonaws.com',
#               'verify_ssl': False,
#               'username': 'AWS',
#               'api_version': 2}
#
#     r = RegistryConnector(tnx, config)
#     a = r.get_tags('spaceone/server-mockup')
#     print(a)
