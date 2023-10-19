DATABASE_AUTO_CREATE_INDEX = True
DATABASES = {
    'default': {
        'db': 'repository',
        'host': 'localhost',
        'port': 27017,
        'username': 'repository',
        'password': ''
    }
}

CACHES = {
    'default': {},
    'local': {
        'backend': 'spaceone.core.cache.local_cache.LocalCache',
        'max_size': 128,
        'ttl': 300
    }
}

CONNECTORS = {
    'AWSPrivateECRConnector': {
        'aws_access_key_id': '',
        'aws_secret_access_key': '',
        'region_name': ''
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

REGISTRY_URL_MAP = {
    'DOCKER_HUB': 'registry.hub.docker.com',
    'AWS_PRIVATE_ECR': 'private.ecr.aws',
    'HARBOR': ''    # default ""
}

# Use managed repository (Read Only), if you can not use plugin marketplace
ENABLE_MANAGED_REPOSITORY = False
DEFAULT_REGISTRY = "DOCKER_HUB" # DOCKER_HUB | AWS_PRIVATE_ECR | HARBOR

ROOT_TOKEN = ""
ROOT_TOKEN_INFO = {}

MANAGED_REGISTRY_TYPE = 'DOCKER_HUB'
MANAGED_REGISTRY_CONFIG = {}
MANAGED_PLUGIN_IMAGE_PREFIX = 'spaceone'
