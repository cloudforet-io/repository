import abc
import requests
import logging
import boto3
from distutils.version import StrictVersion

from spaceone.core.connector import BaseConnector
from spaceone.repository.error import *

__all__ = ['DockerHubConnector', 'AWSPrivateECRConnector', 'HarborConnector']

_LOGGER = logging.getLogger(__name__)
_DEFAULT_PAGE_SIZE = 10


class RegistryConnector(BaseConnector):

    @abc.abstractmethod
    def get_tags(self, registry_url, image, config):
        pass


class DockerHubConnector(RegistryConnector):

    def get_tags(self, registry_url, image, config):
        url = f'https://{registry_url}/v2/repositories/{image}/tags'

        response = requests.get(url)

        if response.status_code == 200:
            image_tags = []
            results = response.json().get('results', [])
            for tag in results:
                image_tags.append(tag['name'])

            return image_tags

        else:
            raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type='DOCKER_HUB', image=image)


class HarborConnector(RegistryConnector):

    def get_tags(self, registry_url, image, config):
        base_url = self.config.get('base_url')
        verify = self.config.get('verify', True)

        headers = {
            'authorization': f'Basic {self.config["token"]}'
        }

        url = f'{base_url}/v2/{image}/tags/list'

        response = requests.get(url, headers=headers, verify=verify)

        if response.status_code == 200:
            image_tags = response.json().get('tags', [])
            image_tags.sort(key=StrictVersion, reverse=True)
            return image_tags
        else:
            _LOGGER.error(f'[get_tags] request error: {response.json()}')

        raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type='HARBOR', image=image)


class AWSPrivateECRConnector(RegistryConnector):
    _DEFAULT_REGION_NAME = 'ap-northeast-2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        aws_access_key_id = self.config.get('aws_access_key_id')
        aws_secret_access_key = self.config.get('aws_secret_access_key')

        if not all([aws_access_key_id, aws_secret_access_key]):
            raise ERROR_CONNECTOR_CONFIGURATION(connector='AWSPrivateECRConnector')

        self.client = boto3.client('ecr',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   region_name=self._DEFAULT_REGION_NAME)

    def get_tags(self, registry_url, image, config):

        account_id = config.get('account_id')

        try:
            response = self.client.describe_images(repositoryName=image, registryId=account_id)

            image_tags = []
            images_info = response.get('imageDetails', [])
            sorted_images_info = sorted(images_info, key=lambda k: k['imagePushedAt'], reverse=True)
            for image_info in sorted_images_info:
                image_tags.extend(image_info['imageTags'])

            return image_tags

        except Exception as e:
            _LOGGER.error(f'[get_tags] boto3 describe_image_tags error: {e}')
            raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type='AWS_PRIVATE_ECR', image=image)


if __name__ == '__main__':
    docker_hub_conn = DockerHubConnector()
    tags = docker_hub_conn.get_tags('registry.hub.docker.com', 'spaceone/repository', {})
    print(tags)
