DATABASE_AUTO_CREATE_INDEX = True
DATABASE_SUPPORT_AWS_DOCUMENT_DB = False
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
        'ttl': 86400
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
    'IdentityConnector': {
    },
    'RepositoryConnector': {
    },
    'SecretConnector': {
    }
}


HANDLERS = {
}

# Docker Registry Base URL: https://index.docker.io/v1/
REGISTRY_URL=""

ENDPOINTS = {
}

LOGGING = {
}

LOG = {
}

################################################################
# SecretConnector needs acess to Domain root's Secret Service
################################################################
ROOT_TOKEN = ""
ROOT_TOKEN_INFO = {}

