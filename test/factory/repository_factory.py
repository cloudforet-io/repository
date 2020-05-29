import factory

from spaceone.core import utils
from spaceone.repository.model.repository_model import Repository


class RepositoryFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Repository

    repository_id = factory.LazyAttribute(lambda o: utils.generate_id('repo'))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    repository_type = 'local'
    state = 'ENABLED'
    endpoint = ''
    version = ''
    secret_id = ''
    created_at = factory.Faker('date_time')
    deleted_at = None
