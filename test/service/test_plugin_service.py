import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.transaction import Transaction
from spaceone.repository.error.plugin import *
from spaceone.repository.service.plugin_service import PluginService
from spaceone.repository.model.plugin_model import Plugin
from spaceone.repository.manager.plugin_manager.local_plugin_manager import LocalPluginManager
from spaceone.repository.manager.identity_manager import IdentityManager
from spaceone.repository.connector.registry_connector import RegistryConnector
from spaceone.repository.info.plugin_info import *
from spaceone.repository.info.common_info import StatisticsInfo
from test.factory.plugin_factory import PluginFactory
from test.factory.repository_factory import RepositoryFactory


class TestPluginService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.repository')
        config.set_service_config()
        config.set_global(MOCK_MODE=True)
        connect('test', host='mongomock://localhost')

        cls.repository_vo = RepositoryFactory(repository_type='local')
        cls.repository_id = cls.repository_vo.repository_id
        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'repository',
            'api_class': 'Plugin'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all plugins')
        plugin_vos = Plugin.objects.filter()
        plugin_vos.delete()

    @patch.object(LocalPluginManager, '_get_registry_url', return_value='registry.hub.docker.com')
    def test_register_plugin(self, *args):
        params = {
            'name': 'google_oauth2',
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
            'domain_id': self.domain_id
        }

        self.transaction.method = 'register'
        plugin_svc = PluginService(transaction=self.transaction)
        plugin_vo = plugin_svc.register(params.copy())

        print_data(plugin_vo.to_dict(), 'test_register_plugin')
        PluginInfo(plugin_vo)

        self.assertIsInstance(plugin_vo, Plugin)
        self.assertEqual(params['name'], plugin_vo.name)
        self.assertEqual(params['image'], plugin_vo.image)
        self.assertIsNotNone(plugin_vo.registry_url)
        self.assertEqual(params['service_type'], plugin_vo.service_type)
        self.assertEqual(params['provider'], plugin_vo.provider)
        self.assertEqual(params.get('capability', {}), plugin_vo.capability)
        self.assertEqual(params.get('template', {}), plugin_vo.template)
        self.assertEqual(params.get('labels', []), plugin_vo.labels)
        self.assertEqual(params['tags'], plugin_vo.tags)
        self.assertEqual(params['domain_id'], plugin_vo.domain_id)

    def test_register_plugin_invalid_template(self, *args):
        params = {
            'name': 'google_oauth2',
            'service_type': 'identity.domain',
            'image': 'spaceone/googleoauth2',
            'template': {
                'options': {
                    'schema': {
                        'type': 'invalid_type',
                        'properties': 'invalid_properties_type'
                    }
                }
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'register'
        plugin_svc = PluginService(transaction=self.transaction)

        with self.assertRaises(ERROR_INVALID_TEMPLATE_SCHEMA):
            plugin_svc.register(params)

    def test_register_plugin_invalid_capability(self, *args):
        params = {
            'name': 'google_oauth2',
            'service_type': 'identity.domain',
            'image': 'spaceone/googleoauth2',
            'capability': {
                'supported_schema': {}
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'register'
        plugin_svc = PluginService(transaction=self.transaction)

        # with self.assertRaises(ERROR_INVALID_PARAMETER):
        #     plugin_svc.register(params)

    def test_register_plugin_invalid_service_type(self, *args):
        params = {
            'name': 'google_oauth2',
            'service_type': 'custom.identity.domain',
            'image': 'spaceone/googleoauth2',
            'domain_id': self.domain_id
        }

        self.transaction.method = 'register'
        plugin_svc = PluginService(transaction=self.transaction)

        # with self.assertRaises(ERROR_INVALID_PARAMETER):
        #     plugin_svc.register(params)

    @patch.object(IdentityManager, 'get_project', return_value=None)
    @patch.object(LocalPluginManager, '_get_registry_url', return_value='registry.hub.docker.com')
    def test_register_plugin_with_project(self, *args):
        params = {
            'name': 'google_oauth2',
            'service_type': 'identity.domain',
            'image': 'spaceone/googleoauth2',
            'project_id': utils.generate_id('project'),
            'domain_id': self.domain_id
        }

        self.transaction.method = 'register'
        plugin_svc = PluginService(transaction=self.transaction)
        plugin_vo = plugin_svc.register(params.copy())

        print_data(plugin_vo.to_dict(), 'test_register_plugin_with_project')
        PluginInfo(plugin_vo)

        self.assertIsInstance(plugin_vo, Plugin)
        self.assertEqual(plugin_vo.project_id, params['project_id'])

    def test_update_plugin(self, *args):
        new_plugin_vo = PluginFactory(domain_id=self.domain_id)
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'name': 'google_oauth3',
            'provider': 'google_cloud',
            'capability': {
                'supported_schema': ['aws_access_key2', 'aws_assume_role2']
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
                            }
                        },
                        'required': ['domain']
                    }
                }
            },
            'labels': ['ee', 'ff'],
            'tags': {
                'update_key': 'update_value'
            },
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        plugin_svc = PluginService(transaction=self.transaction)
        plugin_vo = plugin_svc.update(params.copy())

        print_data(plugin_vo.to_dict(), 'test_update_plugin')
        PluginInfo(plugin_vo)

        self.assertIsInstance(plugin_vo, Plugin)
        self.assertEqual(new_plugin_vo.plugin_id, plugin_vo.plugin_id)
        self.assertEqual(params['name'], plugin_vo.name)
        self.assertEqual(params['provider'], plugin_vo.provider)
        self.assertEqual(params.get('capability', {}), plugin_vo.capability)
        self.assertEqual(params.get('template', {}), plugin_vo.template)
        self.assertEqual(params.get('labels', []), plugin_vo.labels)
        self.assertEqual(params['tags'], plugin_vo.tags)

    def test_delete_plugin(self, *args):
        new_plugin_vo = PluginFactory(domain_id=self.domain_id)
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        plugin_svc = PluginService(transaction=self.transaction)
        result = plugin_svc.deregister(params)

        self.assertIsNone(result)

    def test_enable_plugin(self, *args):
        new_plugin_vo = PluginFactory(domain_id=self.domain_id, state='DISABLED')
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'enable'
        plugin_svc = PluginService(transaction=self.transaction)
        plugin_vo = plugin_svc.enable(params.copy())

        print_data(plugin_vo.to_dict(), 'test_enable_plugin')
        PluginInfo(plugin_vo)

        self.assertIsInstance(plugin_vo, Plugin)
        self.assertEqual(new_plugin_vo.plugin_id, plugin_vo.plugin_id)
        self.assertEqual('ENABLED', plugin_vo.state)

    def test_disable_plugin(self, *args):
        new_plugin_vo = PluginFactory(domain_id=self.domain_id, state='ENABLED')
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'disable'
        plugin_svc = PluginService(transaction=self.transaction)
        plugin_vo = plugin_svc.disable(params.copy())

        print_data(plugin_vo.to_dict(), 'test_disable_plugin')
        PluginInfo(plugin_vo)

        self.assertIsInstance(plugin_vo, Plugin)
        self.assertEqual(new_plugin_vo.plugin_id, plugin_vo.plugin_id)
        self.assertEqual('DISABLED', plugin_vo.state)

    @patch.object(RegistryConnector, 'get_tags', return_value=['1.0', '2.0'])
    def test_get_versions(self, *args):
        new_plugin_vo = PluginFactory(domain_id=self.domain_id)
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get_versions'
        plugin_svc = PluginService(transaction=self.transaction)
        version_list = plugin_svc.get_versions(params)

        print_data(version_list, 'test_get_versions')
        VersionsInfo(version_list)

        self.assertIsInstance(version_list, list)

    @patch.object(RegistryConnector, 'get_tags', return_value=['1.0', '2.0'])
    def test_get_versions_from_multi_repositories(self, *args):
        new_repository_vo = RepositoryFactory(repository_type='remote')
        new_plugin_vo = PluginFactory(domain_id=self.domain_id, repository=new_repository_vo)
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get_versions'
        plugin_svc = PluginService(transaction=self.transaction)
        version_list = plugin_svc.get_versions(params)

        print_data(version_list, 'test_get_versions')
        VersionsInfo(version_list)

        self.assertIsInstance(version_list, list)

    def test_get_plugin(self, *args):
        new_plugin_vo = PluginFactory(domain_id=self.domain_id)
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        plugin_svc = PluginService(transaction=self.transaction)
        plugin_vo = plugin_svc.get(params)

        print_data(plugin_vo.to_dict(), 'test_get_plugin')
        PluginInfo(plugin_vo)

        self.assertIsInstance(plugin_vo, Plugin)

    def test_get_plugin_from_multi_repositories(self, *args):
        new_repository_vo = RepositoryFactory(repository_type='remote')
        new_plugin_vo = PluginFactory(domain_id=self.domain_id, repository=new_repository_vo)
        params = {
            'plugin_id': new_plugin_vo.plugin_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        plugin_svc = PluginService(transaction=self.transaction)
        plugin_vo = plugin_svc.get(params)

        print_data(plugin_vo.to_dict(), 'test_get_plugin_from_multi_repositories')
        PluginInfo(plugin_vo)

        self.assertIsInstance(plugin_vo, Plugin)

    def test_list_plugins_by_plugin_id(self, *args):
        plugin_vos = PluginFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), plugin_vos))

        params = {
            'plugin_id': plugin_vos[0].plugin_id,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        plugin_svc = PluginService()
        plugins_vos, total_count = plugin_svc.list(params)
        PluginsInfo(plugin_vos, total_count)

        self.assertEqual(len(plugins_vos), 1)
        self.assertIsInstance(plugins_vos[0], Plugin)
        self.assertEqual(total_count, 1)

    def test_list_plugins_by_name(self, *args):
        plugin_vos = PluginFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), plugin_vos))

        params = {
            'name': plugin_vos[0].name,
            'repository_id': self.repository_id,
            'domain_id': self.domain_id
        }

        plugin_svc = PluginService()
        plugins_vos, total_count = plugin_svc.list(params)

        self.assertEqual(len(plugins_vos), 1)
        self.assertIsInstance(plugins_vos[0], Plugin)
        self.assertEqual(total_count, 1)

    def test_list_plugins_by_repository(self, *args):
        new_repository_vo = RepositoryFactory(repository_type='local')
        plugin_vos = PluginFactory.build_batch(3, repository=new_repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), plugin_vos))

        plugin_vos = PluginFactory.build_batch(7, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), plugin_vos))

        params = {
            'repository_id': new_repository_vo.repository_id,
            'domain_id': self.domain_id
        }

        plugin_svc = PluginService()
        plugins_vos, total_count = plugin_svc.list(params)
        PluginsInfo(plugin_vos, total_count)

        self.assertEqual(len(plugins_vos), 3)
        self.assertIsInstance(plugins_vos[0], Plugin)
        self.assertEqual(total_count, 3)

    def test_list_plugins_by_tag(self, *args):
        PluginFactory(tags={'tag_key_1': 'tag_value_1'}, repository=self.repository_vo,
                      domain_id=self.domain_id)
        plugin_vos = PluginFactory.build_batch(9, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), plugin_vos))

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

        plugin_svc = PluginService()
        plugins_vos, total_count = plugin_svc.list(params)
        PluginsInfo(plugin_vos, total_count)

        self.assertEqual(len(plugins_vos), 1)
        self.assertIsInstance(plugins_vos[0], Plugin)
        self.assertEqual(total_count, 1)

    def test_stat_plugin(self, *args):
        plugin_vos = PluginFactory.build_batch(10, repository=self.repository_vo,
                                               domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), plugin_vos))

        params = {
            'domain_id': self.domain_id,
            'repository_id': self.repository_vo.repository_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'plugin_id',
                            'name': 'Id'
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
        plugin_svc = PluginService(transaction=self.transaction)
        values = plugin_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_plugin')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
