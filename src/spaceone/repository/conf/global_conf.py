DATABASES = {
    "default": {
        # 'db': 'repository',
        # 'host': 'localhost',
        # 'port': 27017,
        # 'username': 'repository',
        # 'password': ''
    }
}

CACHES = {"default": {}}

CONNECTORS = {
    "AWSPrivateECRConnector": {
        "aws_access_key_id": "",
        "aws_secret_access_key": "",
        "region_name": "",
        "account_id": "",
    },
    "DockerHubConnector": {},
    "HarborConnector": {
        "base_url": "",
        "token": "",
        "image_prefix": "",
        "verify": True,
    },
    "GithubContainerRegistryConnector": {
        "github_token": "",
        "owner_type": "",  # USER | ORGANIZATION
    },
    "GCPPrivateGCRConnector": {
        "location": "",  # GCP 리전 설정
        "project_id": "",  # GCP 프로젝트 ID (선택사항, 기본값 사용 시 비워둠)
        "repository_id":"",
        "service_account_key": ""
    },
    "SpaceConnector": {
        "backend": "spaceone.core.connector.space_connector.SpaceConnector",
        "endpoints": {"identity": "grpc+ssl://localhost:50051"},
    }
}

# 2. 인증 핸들러 설정 (필수)
HANDLERS = {
    "authentication": [{
        "backend": "spaceone.core.handler.authentication_handler.AuthenticationGRPCHandler",
    }],
    "authorization": [{
        "backend": "spaceone.core.handler.authorization_handler.AuthorizationGRPCHandler",
        "uri": ""
    }],
    "mutation": [{
        "backend": "spaceone.core.handler.mutation_handler.SpaceONEMutationHandler"
    }],
    "event": []
}

REGISTRY_INFO = {
    "DOCKER_HUB": {"url": "registry.hub.docker.com"},
    "AWS_PRIVATE_ECR": {"url": "", "image_pull_secrets": ""},
    "HARBOR": {"url": "", "image_pull_secrets": ""},
    "GITHUB": {"url": "ghcr.io"},
    "GCP_PRIVATE_GCR": {"url": ""},
}

# Use managed repository (Read Only), if you can not use plugin marketplace
ENABLE_MANAGED_REPOSITORY = False
DEFAULT_REGISTRY = "DOCKER_HUB"  # DOCKER_HUB | AWS_PRIVATE_ECR | HARBOR | GCP_PRIVATE_GCR

ROOT_TOKEN = ""
ROOT_TOKEN_INFO = {}

MANAGED_REGISTRY_TYPE = "DOCKER_HUB"
MANAGED_REGISTRY_CONFIG = {}
MANAGED_PLUGIN_IMAGE_PREFIX = "cloudforet"

# System Token
TOKEN = ""

REPOSITORIES = [
    {
        "repository_id": "repo-managed",
        "name": "Cloudforet Official",
        "repository_type": "MANAGED",
    },
    # {
    #     "repository_id": "repo-remote",
    #     "name": "Marketplace",
    #     "repository_type": "REMOTE",
    #     "endpoint": "grpc://localhost:50051",
    #     "token": "",
    # },
    {
        "repository_id": "repo-local",
        "name": "Private",
        "repository_type": "LOCAL",
    },
]
