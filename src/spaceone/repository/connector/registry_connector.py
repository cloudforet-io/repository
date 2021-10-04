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
    def get_tags(self, registry_url, image, config):
        pass


class DockerHubConnector(RegistryConnector):

    _DEFAULT_PAGE_SIZE = 1024

    def get_tags(self, registry_url, image, config):
        url = f'https://{registry_url}/v2/repositories/{image}/tags?page_size={self._DEFAULT_PAGE_SIZE}'

        response = requests.get(url)

        if response.status_code == 200:
            image_tags = []
            results = response.json().get('results', [])
            for tag in results:
                image_tags.append(tag['name'])

            return image_tags

        else:
            raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type='DOCKER_HUB', image=image)


class AWSPublicECRConnector(RegistryConnector):

    _DEFAULT_REGION_NAME = 'us-east-1'

    def __init__(self, transaction, config):
        super().__init__(transaction, config)

        aws_access_key_id = self.config.get('aws_access_key_id')
        aws_secret_access_key = self.config.get('aws_secret_access_key')

        if not all([aws_access_key_id, aws_secret_access_key]):
            raise ERROR_CONNECTOR_CONFIGURATION(connector='AWSECRConnector')

        self.client = boto3.client('ecr-public',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   region_name=self._DEFAULT_REGION_NAME)

    def get_tags(self, registry_url, image, config):
        # TODO: change docker registry v2 api

        account_id = config.get('account_id')
        ecr_image = self._parse_ecr_image(image)

        try:
            response = self.client.describe_images(repositoryName=ecr_image, registryId=account_id)

            image_tags = []
            results = response.get('imageTagDetails', [])
            sorted_results = sorted(results, key=lambda k: k['createdAt'], reverse=True)
            for tag in sorted_results:
                image_tags.append(tag['imageTag'])

            return image_tags

        except Exception as e:
            _LOGGER.error(f'[get_tags] boto3 describe_image_tags error: {e}')
            raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type='AWS_PUBLIC_ECR', image=image)

    @staticmethod
    def _parse_ecr_image(image):
        return '/'.join(image.split('/')[1:])


if __name__ == '__main__':
    docker_hub_conn = DockerHubConnector()
    tags = docker_hub_conn.get_tags('registry.hub.docker.com', 'spaceone/repository')
    print(tags)
