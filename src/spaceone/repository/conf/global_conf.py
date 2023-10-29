DATABASES = {
    'default': {
        # 'db': 'repository',
        # 'host': 'localhost',
        # 'port': 27017,
        # 'username': 'repository',
        # 'password': ''
    }
}

CACHES = {
    'default': {}
}

CONNECTORS = {
    'AWSPrivateECRConnector': {
        'aws_access_key_id': '',
        'aws_secret_access_key': '',
        'region_name': '',
        'account_id': ''
    },
    'DockerHubConnector': {},
    'HarborConnector': {
        'base_url': '',
        'token': '',
        'image_prefix': '',
        'verify': True
    },
    'RemoteRepositoryConnector': {},
    'SpaceConnector': {
        'backend': 'spaceone.core.connector.space_connector.SpaceConnector',
        'endpoints': {
            'identity': 'grpc://identity:50051',
            'secret': 'grpc://secret:50051'
        }
    }
}

REGISTRY_INFO = {
    'DOCKER_HUB': {
        'url': 'registry.hub.docker.com'
    },
    'AWS_PRIVATE_ECR': {
        'url': '',
        'image_pull_secrets': ''
    },
    'HARBOR': {
        'url': '',
        'image_pull_secrets': ''
    }
}

# Use managed repository (Read Only), if you can not use plugin marketplace
ENABLE_MANAGED_REPOSITORY = False
DEFAULT_REGISTRY = "DOCKER_HUB"  # DOCKER_HUB | AWS_PRIVATE_ECR | HARBOR

ROOT_TOKEN = ""
ROOT_TOKEN_INFO = {}

MANAGED_REGISTRY_TYPE = 'DOCKER_HUB'
MANAGED_REGISTRY_CONFIG = {}
MANAGED_PLUGIN_IMAGE_PREFIX = 'spaceone'
