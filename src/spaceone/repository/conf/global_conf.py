DATABASE_AUTO_CREATE_INDEX = True
DATABASE_CASE_INSENSITIVE_INDEX = False
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
    'RegistryConnector': {
        'host': 'https://registry.hub.docker.com',
        'verify_ssl': False,
        'api_version': 1,
        'username': '',
        'password': '',
        'auth_service_url': '',
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


HANDLERS = {
}

# Docker Registry Base URL: https://index.docker.io/v1/
REGISTRY_URL = ""

ENDPOINTS = {
}

LOGGING = {
}

LOG = {
}

ROOT_TOKEN = ""
ROOT_TOKEN_INFO = {}

