import factory

from spaceone.core import utils
from spaceone.repository.model.schema_model import Schema
from test.factory.repository_factory import RepositoryFactory


class SchemaFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Schema

    name = factory.LazyAttribute(lambda o: utils.random_string())
    service_type = 'secret.credentials'
    schema = {
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
    labels = ['aa', 'bb']
    tags = [
        {
            'key': 'tag_key',
            'value': 'tag_value'
        }
    ]

    repository = factory.SubFactory(RepositoryFactory)
    project_id = None
    domain_id = utils.generate_id('domain')
    created_at = factory.Faker('date_time')
    updated_at = factory.Faker('date_time')
