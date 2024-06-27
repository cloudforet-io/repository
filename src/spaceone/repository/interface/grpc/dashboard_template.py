from spaceone.api.repository.v1 import dashboard_template_pb2, dashboard_template_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class DashboardTemplate(BaseAPI, dashboard_template_pb2_grpc.DashboardTemplateServicer):

    pb2 = dashboard_template_pb2
    pb2_grpc = dashboard_template_pb2_grpc

    def register(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('DashboardTemplateService', metadata) as template_svc:
            template_data = template_svc.register(params)
            return self.locator.get_info('DashboardTemplateInfo', template_data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('DashboardTemplateService', metadata) as template_svc:
            template_data = template_svc.update(params)
            return self.locator.get_info('DashboardTemplateInfo', template_data)

    def deregister(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('DashboardTemplateService', metadata) as template_svc:
            template_svc.deregister(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('DashboardTemplateService', metadata) as template_svc:
            template_data = template_svc.enable(params)
            return self.locator.get_info('DashboardTemplateInfo', template_data)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('DashboardTemplateService', metadata) as template_svc:
            template_data = template_svc.disable(params)
            return self.locator.get_info('DashboardTemplateInfo', template_data)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('DashboardTemplateService', metadata) as template_svc:
            template_data = template_svc.get(params)
            return self.locator.get_info('DashboardTemplateInfo', template_data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('DashboardTemplateService', metadata) as template_svc:
            templates_data, total_count = template_svc.list(params)
            return self.locator.get_info('DashboardTemplatesInfo', templates_data, total_count, minimal=self.get_minimal(params))

