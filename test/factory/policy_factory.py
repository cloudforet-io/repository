import factory

from spaceone.core import utils
from spaceone.repository.model.policy_model import Policy
from test.factory.repository_factory import RepositoryFactory


class PolicyFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Policy

    policy_id = factory.LazyAttribute(lambda o: utils.generate_id('policy'))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    permissions = [
        'identity.Domain.get',
        'identity.Domain.list',
        'identity.ProjectGroup.*',
        'identity.Project.*',
        'identity.User.*',
    ]
    labels = ['aa', 'bb']
    tags = {
        'key': 'value'
    }

    repository = factory.SubFactory(RepositoryFactory)
    project_id = None
    domain_id = utils.generate_id('domain')
    created_at = factory.Faker('date_time')
