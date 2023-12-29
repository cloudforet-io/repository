from spaceone.api.repository.v1 import repository_pb2, repository_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Repository(BaseAPI, repository_pb2_grpc.RepositoryServicer):
    pb2 = repository_pb2
    pb2_grpc = repository_pb2_grpc

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        with self.locator.get_service("RepositoryService", metadata) as repo_svc:
            repos_info = repo_svc.list(params)
            return self.locator.get_info(
                "RepositoriesInfo",
                repos_info,
                minimal=self.get_minimal(params),
            )
