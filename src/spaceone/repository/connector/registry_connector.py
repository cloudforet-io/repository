import abc
import requests
import logging
import boto3
from packaging.version import parse
import base64
import json
from google.oauth2 import service_account
from google.cloud import artifactregistry_v1

from spaceone.core.connector import BaseConnector
from spaceone.repository.error import *

__all__ = [
    "DockerHubConnector",
    "AWSPrivateECRConnector",
    "HarborConnector",
    "GithubContainerRegistryConnector",
    "GCPPrivateGCRConnector",
]

_LOGGER = logging.getLogger(__name__)
_DEFAULT_PAGE_SIZE = 10


class RegistryConnector(BaseConnector):
    @abc.abstractmethod
    def get_tags(self, registry_url, image):
        pass


class DockerHubConnector(RegistryConnector):
    def get_tags(self, registry_url, image):
        url = f"https://{registry_url}/v2/repositories/{image}/tags"

        response = requests.get(url)

        if response.status_code == 200:
            image_tags = []
            results = response.json().get("results", [])
            for tag in results:
                image_tags.append(tag["name"])

            return image_tags

        else:
            raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type="DOCKER_HUB", image=image)


class HarborConnector(RegistryConnector):
    def get_tags(self, registry_url, image):
        base_url = self.config.get("base_url")
        verify = self.config.get("verify", True)

        headers = {"authorization": f'Basic {self.config["token"]}'}

        url = f"{base_url}/v2/{image}/tags/list"

        response = requests.get(url, headers=headers, verify=verify)

        if response.status_code == 200:
            image_tags = response.json().get("tags", [])
            image_tags.sort(key=parse, reverse=True)
            return image_tags
        else:
            _LOGGER.error(f"[get_tags] request error: {response.json()}")

        raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type="HARBOR", image=image)


class AWSPrivateECRConnector(RegistryConnector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        aws_access_key_id = self.config.get("aws_access_key_id")
        aws_secret_access_key = self.config.get("aws_secret_access_key")
        region_name = self.config.get("region_name")

        if not all([aws_access_key_id, aws_secret_access_key]):
            raise ERROR_CONNECTOR_CONFIGURATION(connector="AWSPrivateECRConnector")

        self.client = boto3.client(
            "ecr",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def get_tags(self, registry_url, image):
        try:
            paginator = self.client.get_paginator("describe_images")
            response_iterator = paginator.paginate(
                repositoryName=image, registryId=self.config.get("account_id")
            )
            images_info = []
            for data in response_iterator:
                images_info.extend(data.get("imageDetails", []))

            image_tags = []
            sorted_images_info = sorted(
                images_info, key=lambda k: k["imagePushedAt"], reverse=True
            )
            for image_info in sorted_images_info:
                if "imageTags" in image_info:
                    image_tags.extend(image_info["imageTags"])

            return image_tags

        except Exception as e:
            _LOGGER.error(f"[get_tags] boto3 describe_image_tags error: {e}")
            raise ERROR_NO_IMAGE_IN_REGISTRY(
                registry_type="AWS_PRIVATE_ECR", image=image
            )


class GithubContainerRegistryConnector(RegistryConnector):
    def get_tags(self, registry_url, image):
        owner_type = self.config.get("owner_type")
        github_token = self.config.get("github_token")
        name, package_name = image.split("/", 1)
        registry_url = "api.github.com"

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"token {github_token}",
            "X-Github-Api-Version": "2022-11-28",
        }
        if owner_type == "USER":
            url = f"https://{registry_url}/user/packages/container/{package_name}/versions"
        else:
            url = f"https://api.github.com/orgs/{name}/packages/container/{package_name}/versions"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            image_tags = []
            results = response.json()
            for result in results:
                _tags = result.get("metadata", {}).get("container", {}).get("tags", [])
                image_tags.extend(_tags)

            return image_tags

        else:
            raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type="GITHUB", image=image)


class GCPPrivateGCRConnector(RegistryConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # GCP 인증 설정
        credentials = None
        project = None
        repository_id = None
        location = None
        
        # 서비스 계정 키 JSON 사용
        try:
            self.repository_id = self.config.get("repository_id")
            self.location = self.config.get("location")
            
            service_account_key = self.config.get("service_account_key")
            decoded_key = base64.b64decode(service_account_key).decode('utf-8')
            key_info = json.loads(decoded_key)

            credentials = service_account.Credentials.from_service_account_info(key_info)
            project = credentials.project_id
            _LOGGER.info("[GCPPrivateGCRConnector] Using service account key")

        except Exception as e:
            _LOGGER.error(f"[GCPPrivateGCRConnector] Failed to load service account key: {e}")
            raise ERROR_CONNECTOR_CONFIGURATION(connector="GCPPrivateGCRConnector")
        if not credentials:
            raise ERROR_CONNECTOR_CONFIGURATION(connector="GCPPrivateGCRConnector")
        
        # 설정에서 프로젝트 ID 가져오기 (우선순위: 설정 > 자격증명에서 추출)
        config_project_id = self.config.get("project_id")
        if config_project_id:
            project = config_project_id
        
        self.client = artifactregistry_v1.ArtifactRegistryClient(credentials=credentials)
        self.project = project

    def get_tags(self, registry_url, image):
        try:
            # 이미지 경로에서 repository와 package 정보 추출
            # projects/spaceone-aramco-project/locations/asia-northeast3/repositories/space-cloudops/packages/plugin-http-file-cost-datasource
            
            # Artifact Registry API를 사용하여 태그 목록 가져오기
            parent = f"projects/{self.project}/locations/{self.location}/repositories/{self.repository_id}/packages/{image}"
            
            # print(f"#### parent: {parent}")
            
            request = artifactregistry_v1.ListTagsRequest(parent=parent)
            tags_result = self.client.list_tags(request=request)
            
            image_tags = []
            
            for tag in tags_result:
                tag_name = tag.name.split('/')[-1]
                image_tags.append(tag_name)    
        
        
            try:
                image_tags.sort(key=parse, reverse=True)
            except Exception as e:
                _LOGGER.warning(f"[get_tags] Version sorting failed: {e}, using original order")
                pass
            
            return image_tags
        
        except Exception as e:
            _LOGGER.error(f"[get_tags] GCP Artifact Registry error: {e}")
            raise ERROR_NO_IMAGE_IN_REGISTRY(registry_type="GCP_Private_GCR", image=image)



if __name__ == "__main__":
    docker_hub_conn = DockerHubConnector()
    tags = docker_hub_conn.get_tags(
        "registry.hub.docker.com", "cloudforet/repository", {}
    )
