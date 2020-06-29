from spaceone.api.repository.v1 import schema_pb2, schema_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Schema(BaseAPI, schema_pb2_grpc.SchemaServicer):

    pb2 = schema_pb2
    pb2_grpc = schema_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('SchemaService', metadata) as schema_svc:
            schema_data = schema_svc.create(params)
            return self.locator.get_info('SchemaInfo', schema_data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('SchemaService', metadata) as schema_svc:
            schema_data = schema_svc.update(params)
            return self.locator.get_info('SchemaInfo', schema_data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('SchemaService', metadata) as schema_svc:
            schema_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('SchemaService', metadata) as schema_svc:
            schema_data = schema_svc.get(params)
            return self.locator.get_info('SchemaInfo', schema_data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('SchemaService', metadata) as schema_svc:
            schemas_data, total_count = schema_svc.list(params)
            return self.locator.get_info('SchemasInfo', schemas_data, total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SchemaService', metadata) as schema_svc:
            return self.locator.get_info('StatisticsInfo', schema_svc.stat(params))