from spaceone.api.repository.v1 import plugin_pb2, plugin_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Plugin(BaseAPI, plugin_pb2_grpc.PluginServicer):

    pb2 = plugin_pb2
    pb2_grpc = plugin_pb2_grpc

    def register(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugin_data = plugin_svc.register(params)
            return self.locator.get_info('PluginInfo', plugin_data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugin_data = plugin_svc.update(params)
            return self.locator.get_info('PluginInfo', plugin_data)

    def deregister(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugin_svc.deregister(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugin_data = plugin_svc.enable(params)
            return self.locator.get_info('PluginInfo', plugin_data)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugin_data = plugin_svc.disable(params)
            return self.locator.get_info('PluginInfo', plugin_data)

    def get_versions(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            version_list = plugin_svc.get_versions(params)
            return self.locator.get_info('VersionsInfo', version_list)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugin_data = plugin_svc.get(params)
            return self.locator.get_info('PluginInfo', plugin_data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugins_data, total_count = plugin_svc.list(params)
            return self.locator.get_info('PluginsInfo', plugins_data, total_count) 

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            return self.locator.get_info('StatisticsInfo', plugin_svc.stat(params))