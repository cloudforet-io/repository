import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.model.mongo_model import MongoModel
from spaceone.core.transaction import Transaction
from spaceone.repository.error.schema import *
from spaceone.repository.service.schema_service import SchemaService
from spaceone.repository.model.schema_model import Schema
from spaceone.repository.manager.identity_manager import IdentityManager
from spaceone.repository.info.schema_info import *
from spaceone.repository.info.common_info import StatisticsInfo
from test.factory.schema_factory import SchemaFactory
from test.factory.repository_factory import RepositoryFactory


class TestSchemaService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.repository')
        connect('test', host='mongomock://localhost')

        cls.repository_vo = RepositoryFactory(repository_type='local')
        cls.repository_id = cls.repository_vo.repository_id
        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'repository',
            'api_class': 'Schema'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(MongoModel, 'connect', return_value=None)
    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all schemas')
        schema_vos = Schema.objects.filter()
        schema_vos.delete()

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_schema(self, *args):
        params = {
            'name': 'aws_access_key',
            'service_type': 'secret.credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'aws_access_key_id': {
                        'title': 'AWS Access Key',
                        'type': 'string',
                        'minLength': 4
                    },
                    'aws_secret_access_key': {
                        'title': 'AWS Secret Key',
                        'type': 'string',
                        'minLength': 4
                    },
                    'region_name': {
                        'title': "Region",
                        'type': 'string',
                        'minLength': 4,
                        'examples': ['ap-northeast-2']
                    }
                },
                'required': ['aws_access_key_id', 'aws_secret_access_key']
            },
            'labels': ['cc', 'dd'],
            'tags': {
                'tag_key': 'tag_value'
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        schema_svc = SchemaService(transaction=self.transaction)
        schema_vo = schema_svc.create(params.copy())

        print_data(schema_vo.to_dict(), 'test_create_schema')
        SchemaInfo(schema_vo)

        self.assertIsInstance(schema_vo, Schema)
        self.assertEqual(params['name'], schema_vo.name)
        self.assertEqual(params['service_type'], schema_vo.service_type)
        self.assertEqual(params.get('schema', {}), schema_vo.schema)
        self.assertEqual(params.get('labels', []), schema_vo.labels)
        self.assertEqual(params.get('tags', {}), schema_vo.tags)
        self.assertEqual(params['domain_id'], schema_vo.domain_id)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_duplicate_create_schema(self, *args):
        SchemaFactory(domain_id=self.domain_id, repository=self.repository_vo,
                      name='aws_access_key')
        params = {
            'name': 'aws_access_key',
            'service_type': 'secret.credentials',
            'schema': {
                'type': 'object',
                'properties': {}
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        schema_svc = SchemaService(transaction=self.transaction)

        with self.assertRaises(ERROR_NOT_UNIQUE_KEYS):
            schema_svc.create(params)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_schema_invalid_schema(self, *args):
        params = {
            'name': 'aws_access_key',
            'service_type': 'secret.credentials',
            'schema': {
                'type': 'invalid_type',
                'properties': 'invalid_properties_type'
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        schema_svc = SchemaService(transaction=self.transaction)

        with self.assertRaises(ERROR_INVALID_SCHEMA):
            schema_svc.create(params)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_schema_invalid_service_type(self, *args):
        params = {
            'name': 'aws_access_key',
            'service_type': 'custom.secret.credentials',
            'schema': {
                'type': 'object',
                'properties': {}
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        schema_svc = SchemaService(transaction=self.transaction)

        # with self.assertRaises(ERROR_INVALID_PARAMETER):
        #     schema_svc.create(params)

    @patch.object(IdentityManager, 'get_project', return_value=None)
    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_schema_with_project(self, *args):
        params = {
            'name': 'aws_access_key',
            'service_type': 'custom.secret.credentials',
            'schema': {
                'type': 'object',
                'properties': {}
            },
            'project_id': utils.generate_id('project'),
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        schema_svc = SchemaService(transaction=self.transaction)
        schema_vo = schema_svc.create(params.copy())

        print_data(schema_vo.to_dict(), 'test_create_schema_with_project')
        SchemaInfo(schema_vo)

        self.assertIsInstance(schema_vo, Schema)
        self.assertEqual(schema_vo.project_id, params['project_id'])

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_update_schema(self, *args):
        new_schema_vo = SchemaFactory(domain_id=self.domain_id)
        params = {
            'name': new_schema_vo.name,
            'schema': {
                'type': 'object',
                'properties': {
                    'domain': {
                        'title': 'Email Domain',
                        'type': 'string',
                        'minLength': 4,
                        'examples': ['Ex) gmail.com']
                    }
                },
                'required': ['domain']
            },
            'labels': ['ee', 'ff'],
            'tags': {
                'update_key': 'update_value'
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        schema_svc = SchemaService(transaction=self.transaction)
        schema_vo = schema_svc.update(params.copy())

        print_data(schema_vo.to_dict(), 'test_update_schema')
        SchemaInfo(schema_vo)

        self.assertIsInstance(schema_vo, Schema)
        self.assertEqual(params['name'], schema_vo.name)
        self.assertEqual(params.get('schema', {}), schema_vo.schema)
        self.assertEqual(params.get('labels', []), schema_vo.labels)
        self.assertEqual(params.get('tags', {}), schema_vo.tags)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_delete_schema(self, *args):
        new_schema_vo = SchemaFactory(domain_id=self.domain_id)
        params = {
            'name': new_schema_vo.name,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        schema_svc = SchemaService(transaction=self.transaction)
        result = schema_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_schema(self, *args):
        new_schema_vo = SchemaFactory(domain_id=self.domain_id)
        params = {
            'name': new_schema_vo.name,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        schema_svc = SchemaService(transaction=self.transaction)
        schema_vo = schema_svc.get(params)

        print_data(schema_vo.to_dict(), 'test_get_schema')
        SchemaInfo(schema_vo)

        self.assertIsInstance(schema_vo, Schema)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_schema_from_multi_repositories(self, *args):
        new_repository_vo = RepositoryFactory(repository_type='remote')
        new_schema_vo = SchemaFactory(domain_id=self.domain_id, repository=new_repository_vo)
        params = {
            'name': new_schema_vo.name,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        schema_svc = SchemaService(transaction=self.transaction)
        schema_vo = schema_svc.get(params)

        print_data(schema_vo.to_dict(), 'test_get_schema_from_multi_repositories')
        SchemaInfo(schema_vo)

        self.assertIsInstance(schema_vo, Schema)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_schemas_by_name(self, *args):
        schema_vos = SchemaFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), schema_vos))

        params = {
            'name': schema_vos[0].name,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        schema_svc = SchemaService()
        schemas_vos, total_count = schema_svc.list(params)
        SchemasInfo(schema_vos, total_count)

        self.assertEqual(len(schemas_vos), 1)
        self.assertIsInstance(schemas_vos[0], Schema)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_schemas_by_repository(self, *args):
        new_repository_vo = RepositoryFactory(repository_type='local')
        schema_vos = SchemaFactory.build_batch(3, repository=new_repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), schema_vos))

        schema_vos = SchemaFactory.build_batch(7, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), schema_vos))

        params = {
            'repository_id': new_repository_vo.repository_id,
            'domain_id': self.domain_id
        }

        schema_svc = SchemaService()
        schemas_vos, total_count = schema_svc.list(params)
        SchemasInfo(schema_vos, total_count)

        self.assertEqual(len(schemas_vos), 3)
        self.assertIsInstance(schemas_vos[0], Schema)
        self.assertEqual(total_count, 3)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_schemas_by_tag(self, *args):
        SchemaFactory(tags={'tag_key': 'tag_value'}, repository=self.repository_vo,
                      domain_id=self.domain_id)
        schema_vos = SchemaFactory.build_batch(9, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), schema_vos))

        params = {
            'query': {
                'filter': [{
                    'k': 'tags.tag_key',
                    'v': 'tag_value',
                    'o': 'eq'
                }]
            },
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        schema_svc = SchemaService()
        schemas_vos, total_count = schema_svc.list(params)
        SchemasInfo(schema_vos, total_count)

        self.assertEqual(len(schemas_vos), 1)
        self.assertIsInstance(schemas_vos[0], Schema)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_schema(self, *args):
        schema_vos = SchemaFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), schema_vos))

        params = {
            'domain_id': self.domain_id,
            'repository_id': self.repository_vo.repository_id,
            'query': {
                'aggregate': {
                    'group': {
                        'keys': [{
                            'key': 'name',
                            'name': 'Schema'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }]
                    }
                },
                'sort': {
                    'name': 'Count',
                    'desc': True
                }
            }
        }

        self.transaction.method = 'stat'
        schema_svc = SchemaService(transaction=self.transaction)
        values = schema_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_schema')

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_schema_distinct(self, *args):
        schema_vos = SchemaFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), schema_vos))

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
        schema_svc = SchemaService(transaction=self.transaction)
        values = schema_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_schema_distinct')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
