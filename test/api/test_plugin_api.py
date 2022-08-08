import unittest
import copy
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
from spaceone.api.repository.v1 import plugin_pb2
from spaceone.repository.api.v1.plugin import Plugin
from test.factory.plugin_factory import PluginFactory


class _MockPluginService(BaseService):

    def register(self, params):
        params = copy.deepcopy(params)

        return PluginFactory(**params)

    def update(self, params):
        params = copy.deepcopy(params)

        return PluginFactory(**params)

    def deregister(self, params):
        pass

    def enable(self, params):
        return PluginFactory(**params)

    def disable(self, params):
        return PluginFactory(**params)

    def get_versions(self, params):
        return ['1.0.0', '1.1.0']

    def get(self, params):
        return PluginFactory(**params)

    def list(self, params):
        return PluginFactory.build_batch(10, **params), 10


class TestPluginAPI(unittest.TestCase):

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
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_register_plugin(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'service_type': 'identity.domain',
            'image': 'spaceone/googleoauth2',
            'provider': 'aws',
            'capability': {
                'supported_schema': ['aws_access_key', 'aws_assume_role']
            },
            'template': {
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
            },
            'labels': ['cc', 'dd'],
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        plugin_servicer = Plugin()
        plugin_info = plugin_servicer.register({}, {})

        print_message(plugin_info, 'test_register_plugin')
        plugin_data = MessageToDict(plugin_info, preserving_proto_field_name=True)

        self.assertIsInstance(plugin_info, plugin_pb2.PluginInfo)
        self.assertEqual(plugin_info.name, params['name'])
        self.assertEqual(plugin_info.image, params['image'])
        self.assertIsNotNone(plugin_info.registry_url)
        self.assertEqual(plugin_info.service_type, params['service_type'])
        self.assertEqual(plugin_info.provider, params['provider'])
        self.assertDictEqual(MessageToDict(plugin_info.capability), params['capability'])
        self.assertDictEqual(MessageToDict(plugin_info.template), params['template'])
        self.assertListEqual(list(plugin_info.labels), params['labels'])
        self.assertDictEqual(plugin_data['tags'], params['tags'])
        self.assertEqual(plugin_info.domain_id, params['domain_id'])
        self.assertIsNotNone(getattr(plugin_info, 'created_at', None))

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_update_plugin(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'tags': {
                'update_key': 'update_value'
            },
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        plugin_servicer = Plugin()
        plugin_info = plugin_servicer.update({}, {})

        print_message(plugin_info, 'test_update_plugin')
        plugin_data = MessageToDict(plugin_info, preserving_proto_field_name=True)

        self.assertIsInstance(plugin_info, plugin_pb2.PluginInfo)
        self.assertEqual(plugin_info.name, params['name'])
        self.assertDictEqual(plugin_data['tags'], params['tags'])

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_deregister_plugin(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        plugin_servicer = Plugin()
        plugin_info = plugin_servicer.deregister({}, {})

        print_message(plugin_info, 'test_delete_plugin')

        self.assertIsInstance(plugin_info, Empty)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_enable_plugin(self, mock_parse_request, *args):
        params = {
            'plugin_id': utils.generate_id('plugin'),
            'state': 'ENABLED',
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        plugin_servicer = Plugin()
        plugin_info = plugin_servicer.enable({}, {})

        print_message(plugin_info, 'test_enable_plugin')

        self.assertIsInstance(plugin_info, plugin_pb2.PluginInfo)
        self.assertEqual(plugin_info.state, plugin_pb2.PluginInfo.State.ENABLED)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_disable_plugin(self, mock_parse_request, *args):
        params = {
            'plugin_id': utils.generate_id('plugin'),
            'state': 'DISABLED',
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        plugin_servicer = Plugin()
        plugin_info = plugin_servicer.disable({}, {})

        print_message(plugin_info, 'test_disable_plugin')

        self.assertIsInstance(plugin_info, plugin_pb2.PluginInfo)
        self.assertEqual(plugin_info.state, plugin_pb2.PluginInfo.State.DISABLED)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_get_versions(self, mock_parse_request, *args):
        params = {
            'plugin_id': utils.generate_id('plugin'),
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        plugin_servicer = Plugin()
        versions_info = plugin_servicer.get_versions({}, {})

        print_message(versions_info, 'test_get_versions')

        self.assertIsInstance(versions_info, plugin_pb2.VersionsInfo)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_get_plugin(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        plugin_servicer = Plugin()
        plugin_info = plugin_servicer.get({}, {})

        print_message(plugin_info, 'test_get_plugin')

        self.assertIsInstance(plugin_info, plugin_pb2.PluginInfo)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPluginService())
    @patch.object(BaseAPI, 'parse_request')
    def test_list_plugins(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        plugin_servicer = Plugin()
        plugins_info = plugin_servicer.list({}, {})

        print_message(plugins_info, 'test_list_plugin')

        self.assertIsInstance(plugins_info, plugin_pb2.PluginsInfo)
        self.assertIsInstance(plugins_info.results[0], plugin_pb2.PluginInfo)
        self.assertEqual(plugins_info.total_count, 10)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
