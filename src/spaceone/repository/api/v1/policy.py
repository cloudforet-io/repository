from spaceone.api.repository.v1 import policy_pb2, policy_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Policy(BaseAPI, policy_pb2_grpc.PolicyServicer):

    pb2 = policy_pb2
    pb2_grpc = policy_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            policy_data = policy_svc.create(params)
            return self.locator.get_info('PolicyInfo', policy_data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            policy_data = policy_svc.update(params)
            return self.locator.get_info('PolicyInfo', policy_data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            policy_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            policy_data = policy_svc.get(params)
            return self.locator.get_info('PolicyInfo', policy_data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            policies_data, total_count = policy_svc.list(params)
            return self.locator.get_info('PoliciesInfo', policies_data, total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            return self.locator.get_info('StatisticsInfo', policy_svc.stat(params))
