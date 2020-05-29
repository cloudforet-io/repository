from spaceone.api.repository.v1 import repository_pb2, repository_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Repository(BaseAPI, repository_pb2_grpc.RepositoryServicer):

    pb2 = repository_pb2
    pb2_grpc = repository_pb2_grpc

    def register(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('RepositoryService', metadata) as repo_svc:
            repo_vo = repo_svc.register(params)
            return self.locator.get_info('RepositoryInfo', repo_vo)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('RepositoryService', metadata) as repo_svc:
            repo_vo = repo_svc.update(params)
            return self.locator.get_info('RepositoryInfo', repo_vo)

    def deregister(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('RepositoryService', metadata) as repo_svc:
            repo_svc.deregister(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('RepositoryService', metadata) as repo_svc:
            repo_vo = repo_svc.get(params)
            return self.locator.get_info('RepositoryInfo', repo_vo)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service('RepositoryService', metadata) as repo_svc:
            repo_vos, total_count = repo_svc.list(params)
            return self.locator.get_info('RepositoriesInfo', repo_vos, total_count)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('RepositoryService', metadata) as repo_svc:
            return self.locator.get_info('StatisticsInfo', repo_svc.stat(params))
