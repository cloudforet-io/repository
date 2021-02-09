import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.model.mongo_model import MongoModel
from spaceone.core.transaction import Transaction
from spaceone.repository.error.policy import *
from spaceone.repository.service.policy_service import PolicyService
from spaceone.repository.model.policy_model import Policy
from spaceone.repository.manager.identity_manager import IdentityManager
from spaceone.repository.info.policy_info import *
from spaceone.repository.info.common_info import StatisticsInfo
from test.factory.policy_factory import PolicyFactory
from test.factory.repository_factory import RepositoryFactory


class TestPolicyService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.repository')
        connect('test', host='mongomock://localhost')

        cls.repository_vo = RepositoryFactory(repository_type='local')
        cls.repository_id = cls.repository_vo.repository_id
        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'repository',
            'api_class': 'Policy'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(MongoModel, 'connect', return_value=None)
    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all policys')
        policy_vos = Policy.objects.filter()
        policy_vos.delete()

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_policy(self, *args):
        params = {
            'name': 'Domain Admin',
            'permissions': [
                'identity.*',
                'inventory.*',
                'repository.*',
                'secret.*',
                'monitoring.*'
            ],
            'labels': ['cc', 'dd'],
            'tags': [
                {
                    'key': 'tag_key',
                    'value': 'tag_value'
                }
            ],
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        policy_svc = PolicyService(transaction=self.transaction)
        policy_vo = policy_svc.create(params.copy())

        print_data(policy_vo.to_dict(), 'test_create_policy')
        PolicyInfo(policy_vo)

        self.assertIsInstance(policy_vo, Policy)
        self.assertEqual(params['name'], policy_vo.name)
        self.assertEqual(params.get('permissions', []), policy_vo.permissions)
        self.assertEqual(params.get('labels', []), policy_vo.labels)
        self.assertEqual(params.get('tags', {}), policy_vo.to_dict()['tags'])
        self.assertEqual(params['domain_id'], policy_vo.domain_id)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_duplicate_create_policy(self, *args):
        PolicyFactory(domain_id=self.domain_id, repository=self.repository_vo,
                      name='Domain Admin')
        params = {
            'name': 'Domain Admin',
            'permissions': ['*'],
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        policy_svc = PolicyService(transaction=self.transaction)

        with self.assertRaises(ERROR_SAVE_UNIQUE_VALUES):
            policy_svc.create(params)

    @patch.object(IdentityManager, 'get_project', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_policy_with_project(self, *args):
        params = {
            'name': 'Domain Admin',
            'permissions': ['*'],
            'project_id': utils.generate_id('project'),
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        policy_svc = PolicyService(transaction=self.transaction)
        policy_vo = policy_svc.create(params.copy())

        print_data(policy_vo.to_dict(), 'test_create_policy_with_project')
        PolicyInfo(policy_vo)

        self.assertIsInstance(policy_vo, Policy)
        self.assertEqual(policy_vo.project_id, params['project_id'])

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_update_policy(self, *args):
        new_policy_vo = PolicyFactory(domain_id=self.domain_id)
        params = {
            'policy_id': new_policy_vo.policy_id,
            'name': utils.random_string(),
            'permissions': [
                '*'
            ],
            'labels': ['ee', 'ff'],
            'tags': [
                {
                    'key': 'update_key',
                    'value': 'update_value'
                }
            ],
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        policy_svc = PolicyService(transaction=self.transaction)
        policy_vo = policy_svc.update(params.copy())

        print_data(policy_vo.to_dict(), 'test_update_policy')
        PolicyInfo(policy_vo)

        self.assertIsInstance(policy_vo, Policy)
        self.assertEqual(params['name'], policy_vo.name)
        self.assertEqual(params.get('permissions', []), policy_vo.permissions)
        self.assertEqual(params.get('labels', []), policy_vo.labels)
        self.assertEqual(params.get('tags', {}), policy_vo.to_dict()['tags'])

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_policy(self, *args):
        new_policy_vo = PolicyFactory(domain_id=self.domain_id)
        params = {
            'policy_id': new_policy_vo.policy_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        policy_svc = PolicyService(transaction=self.transaction)
        result = policy_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_policy(self, *args):
        new_policy_vo = PolicyFactory(domain_id=self.domain_id)
        params = {
            'policy_id': new_policy_vo.policy_id,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        policy_svc = PolicyService(transaction=self.transaction)
        policy_vo = policy_svc.get(params)

        print_data(policy_vo.to_dict(), 'test_get_policy')
        PolicyInfo(policy_vo)

        self.assertIsInstance(policy_vo, Policy)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_policy_from_multi_repositories(self, *args):
        new_repository_vo = RepositoryFactory(repository_type='remote')
        new_policy_vo = PolicyFactory(domain_id=self.domain_id, repository=new_repository_vo)
        params = {
            'policy_id': new_policy_vo.policy_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        policy_svc = PolicyService(transaction=self.transaction)
        policy_vo = policy_svc.get(params)

        print_data(policy_vo.to_dict(), 'test_get_policy_from_multi_repositories')
        PolicyInfo(policy_vo)

        self.assertIsInstance(policy_vo, Policy)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_policies_by_name(self, *args):
        policy_vos = PolicyFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), policy_vos))

        params = {
            'name': policy_vos[0].name,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        policy_svc = PolicyService()
        policy_vos, total_count = policy_svc.list(params)
        PoliciesInfo(policy_vos, total_count)

        self.assertEqual(len(policy_vos), 1)
        self.assertIsInstance(policy_vos[0], Policy)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_policies_by_repository(self, *args):
        new_repository_vo = RepositoryFactory(repository_type='local')
        policy_vos = PolicyFactory.build_batch(3, repository=new_repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), policy_vos))

        policy_vos = PolicyFactory.build_batch(7, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), policy_vos))

        params = {
            'repository_id': new_repository_vo.repository_id,
            'domain_id': self.domain_id
        }

        policy_svc = PolicyService()
        policy_vos, total_count = policy_svc.list(params)
        PoliciesInfo(policy_vos, total_count)

        self.assertEqual(len(policy_vos), 3)
        self.assertIsInstance(policy_vos[0], Policy)
        self.assertEqual(total_count, 3)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_policies_by_tag(self, *args):
        PolicyFactory(tags=[{'key': 'tag_key_1', 'value': 'tag_value_1'}], repository=self.repository_vo,
                      domain_id=self.domain_id)
        policy_vos = PolicyFactory.build_batch(9, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), policy_vos))

        params = {
            'query': {
                'filter': [{
                    'k': 'tags.tag_key_1',
                    'v': 'tag_value_1',
                    'o': 'eq'
                }]
            },
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        policy_svc = PolicyService()
        policy_vos, total_count = policy_svc.list(params)
        PoliciesInfo(policy_vos, total_count)

        self.assertEqual(len(policy_vos), 1)
        self.assertIsInstance(policy_vos[0], Policy)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_policy(self, *args):
        policy_vos = PolicyFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), policy_vos))

        params = {
            'domain_id': self.domain_id,
            'repository_id': self.repository_vo.repository_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'name',
                            'name': 'Policy'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }]
                    }
                }, {
                    'sort': {
                        'key': 'Count',
                        'desc': True
                    }
                }]
            }
        }

        self.transaction.method = 'stat'
        policy_svc = PolicyService(transaction=self.transaction)
        values = policy_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_policy')

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_policy_distinct(self, *args):
        policy_vos = PolicyFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), policy_vos))

        params = {
            'domain_id': self.domain_id,
            'repository_id': self.repository_vo.repository_id,
            'query': {
                'distinct': 'name',
                'page': {
                    'start': 3,
                    'limit': 4
                }
            }
        }

        self.transaction.method = 'stat'
        policy_svc = PolicyService(transaction=self.transaction)
        values = policy_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_policy_distinct')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
