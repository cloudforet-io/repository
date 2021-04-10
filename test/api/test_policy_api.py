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
from spaceone.api.repository.v1 import policy_pb2
from spaceone.repository.api.v1.policy import Policy
from test.factory.policy_factory import PolicyFactory


class _MockPolicyService(BaseService):

    def create(self, params):
        params = copy.deepcopy(params)
        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return PolicyFactory(**params)

    def update(self, params):
        params = copy.deepcopy(params)
        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return PolicyFactory(**params)

    def delete(self, params):
        pass

    def get(self, params):
        return PolicyFactory(**params)

    def list(self, params):
        return PolicyFactory.build_batch(10, **params), 10


class TestPolicyAPI(unittest.TestCase):

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
    @patch.object(Locator, 'get_service', return_value=_MockPolicyService())
    @patch.object(BaseAPI, 'parse_request')
    def test_create_policy(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'permissions': [
                'inventory.Region.*',
                'inventory.Server.*',
                'inventory.CloudServiceType.*',
                'inventory.CloudService.*',
                'inventory.Collector.get',
                'inventory.Collector.list',
            ],
            'labels': ['cc', 'dd'],
            'tags': {
                utils.random_string(): utils.random_string()
            },
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        policy_servicer = Policy()
        policy_info = policy_servicer.create({}, {})

        print_message(policy_info, 'test_create_policy')
        policy_data = MessageToDict(policy_info, preserving_proto_field_name=True)

        self.assertIsInstance(policy_info, policy_pb2.PolicyInfo)
        self.assertEqual(policy_info.name, params['name'])
        self.assertEqual(list(policy_info.permissions), params['permissions'])
        self.assertListEqual(list(policy_info.labels), params['labels'])
        self.assertDictEqual(policy_data['tags'], params['tags'])
        self.assertEqual(policy_info.domain_id, params['domain_id'])
        self.assertIsNotNone(getattr(policy_info, 'created_at', None))

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPolicyService())
    @patch.object(BaseAPI, 'parse_request')
    def test_update_policy(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'permissions': [
                'inventory.Region.*',
                'inventory.Server.*'
            ],
            'tags': {
                'update_key': 'update_value'
            },
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        policy_servicer = Policy()
        policy_info = policy_servicer.update({}, {})

        print_message(policy_info, 'test_update_policy')
        policy_data = MessageToDict(policy_info, preserving_proto_field_name=True)

        self.assertIsInstance(policy_info, policy_pb2.PolicyInfo)
        self.assertEqual(policy_info.name, params['name'])
        self.assertEqual(list(policy_info.permissions), params['permissions'])
        self.assertDictEqual(policy_data['tags'], params['tags'])

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPolicyService())
    @patch.object(BaseAPI, 'parse_request')
    def test_delete_policy(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        policy_servicer = Policy()
        policy_info = policy_servicer.delete({}, {})

        print_message(policy_info, 'test_delete_policy')

        self.assertIsInstance(policy_info, Empty)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPolicyService())
    @patch.object(BaseAPI, 'parse_request')
    def test_get_policy(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        policy_servicer = Policy()
        policy_info = policy_servicer.get({}, {})

        print_message(policy_info, 'test_get_policy')

        self.assertIsInstance(policy_info, policy_pb2.PolicyInfo)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockPolicyService())
    @patch.object(BaseAPI, 'parse_request')
    def test_list_policies(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        policy_servicer = Policy()
        policies_info = policy_servicer.list({}, {})

        print_message(policies_info, 'test_list_policies')

        self.assertIsInstance(policies_info, policy_pb2.PoliciesInfo)
        self.assertIsInstance(policies_info.results[0], policy_pb2.PolicyInfo)
        self.assertEqual(policies_info.total_count, 10)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
