import functools
from spaceone.api.repository.v1 import repository_pb2

__all__ = ["RepositoryInfo", "RepositoriesInfo"]


def RepositoryInfo(repository_info: dict, minimal=False):
    info = {
        "repository_id": repository_info["repository_id"],
        "name": repository_info["name"],
        "repository_type": repository_info["repository_type"],
    }

    if not minimal:
        info.update(
            {
                "endpoint": repository_info.get("endpoint"),
            }
        )

    return repository_pb2.RepositoryInfo(**info)


def RepositoriesInfo(repos_info, **kwargs):
    return repository_pb2.RepositoriesInfo(
        results=list(map(functools.partial(RepositoryInfo, **kwargs), repos_info)),
    )
