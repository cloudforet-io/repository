import factory

from spaceone.core import utils
from spaceone.repository.model.plugin_model import Plugin
from test.factory.repository_factory import RepositoryFactory


class PluginFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Plugin

    plugin_id = factory.LazyAttribute(lambda o: utils.generate_id('plugin'))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    state = 'ENABLED'
    image = 'spaceone/googleoauth2'
    registry_url = 'registry.hub.docker.com'
    service_type = 'identity.domain'
    provider = 'aws'
    capability = {
        'supported_schema': ['aws_access_key']
    }
    template = {
        'options': {
            'schema': {
                'type': 'object',
                'properties': {
                    'domain': {
                        'title': 'Email Domain',
                        'type': 'string',
                        'minLength': 4,
                        'examples': ['Ex) gmail.com']
                    },
                    'client_id': {
                        'title': 'Client ID',
                        'type': 'string',
                        'minLength': 4,
                        'examples': ['OAuth 2.0 Client ID']
                    }
                },
                'required': ['domain', 'client_id']
            }
        }
    }
    labels = ['aa', 'bb']
    tags = {'tag_key': 'tag_value'}

    repository = factory.SubFactory(RepositoryFactory)
    repository_id = factory.LazyAttribute(lambda o: utils.generate_id('repo'))
    project_id = None
    domain_id = utils.generate_id('domain')
    created_at = factory.Faker('date_time')
    updated_at = factory.Faker('date_time')
