import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect
from google.protobuf.json_format import MessageToDict
from google.protobuf.empty_pb2 import Empty

from spaceone.core.unittest.result import print_message
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.service import BaseService
from spaceone.core.locator import Locator
from spaceone.core.pygrpc import BaseAPI
from spaceone.api.repository.v1 import schema_pb2
from spaceone.repository.api.v1.schema import Schema
from test.factory.schema_factory import SchemaFactory


class _MockSchemaService(BaseService):

    def create(self, params):
        return SchemaFactory(**params)

    def update(self, params):
        return SchemaFactory(**params)

    def delete(self, params):
        pass

    def get(self, params):
        return SchemaFactory(**params)

    def list(self, params):
        return SchemaFactory.build_batch(10, **params), 10


class TestSchemaAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.repository')
        connect('test', host='mongomock://localhost')
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockSchemaService())
    @patch.object(BaseAPI, 'parse_request')
    def test_create_schema(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'service_type': 'secret.credentials',
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
            },
            'labels': ['cc', 'dd'],
            'tags': {
                'tag_key': 'tag_value'
            },
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        schema_servicer = Schema()
        schema_info = schema_servicer.create({}, {})

        print_message(schema_info, 'test_create_schema')

        self.assertIsInstance(schema_info, schema_pb2.SchemaInfo)
        self.assertEqual(schema_info.name, params['name'])
        self.assertEqual(schema_info.service_type, params['service_type'])
        self.assertDictEqual(MessageToDict(schema_info.schema), params['schema'])
        self.assertListEqual(list(schema_info.labels), params['labels'])
        self.assertDictEqual(MessageToDict(schema_info.tags), params['tags'])
        self.assertEqual(schema_info.domain_id, params['domain_id'])
        self.assertIsNotNone(getattr(schema_info, 'created_at', None))

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockSchemaService())
    @patch.object(BaseAPI, 'parse_request')
    def test_update_schema(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'tags': {
                'update_key': 'update_value'
            },
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        schema_servicer = Schema()
        schema_info = schema_servicer.update({}, {})

        print_message(schema_info, 'test_update_schema')

        self.assertIsInstance(schema_info, schema_pb2.SchemaInfo)
        self.assertEqual(schema_info.name, params['name'])
        self.assertDictEqual(MessageToDict(schema_info.tags), params['tags'])

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockSchemaService())
    @patch.object(BaseAPI, 'parse_request')
    def test_delete_schema(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        schema_servicer = Schema()
        schema_info = schema_servicer.delete({}, {})

        print_message(schema_info, 'test_delete_schema')

        self.assertIsInstance(schema_info, Empty)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockSchemaService())
    @patch.object(BaseAPI, 'parse_request')
    def test_get_schema(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        schema_servicer = Schema()
        schema_info = schema_servicer.get({}, {})

        print_message(schema_info, 'test_get_schema')

        self.assertIsInstance(schema_info, schema_pb2.SchemaInfo)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockSchemaService())
    @patch.object(BaseAPI, 'parse_request')
    def test_list_schemas(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        schema_servicer = Schema()
        schemas_info = schema_servicer.list({}, {})

        print_message(schemas_info, 'test_list_schema')

        self.assertIsInstance(schemas_info, schema_pb2.SchemasInfo)
        self.assertIsInstance(schemas_info.results[0], schema_pb2.SchemaInfo)
        self.assertEqual(schemas_info.total_count, 10)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
