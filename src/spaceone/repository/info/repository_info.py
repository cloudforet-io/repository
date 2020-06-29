import functools
from spaceone.api.repository.v1 import repository_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.repository.model.repository_model import Repository

__all__ = ['RepositoryInfo','RepositoriesInfo']


def RepositoryInfo(repository_vo: Repository, minimal=False):
    info = {
        'repository_id': repository_vo.repository_id,
        'name': repository_vo.name,
        'repository_type': repository_vo.repository_type
    }
    if not minimal:
        info.update({
                'endpoint': repository_vo.endpoint,
                'version': repository_vo.version,
                'secret_id': repository_vo.secret_id,
                'created_at': change_timestamp_type(repository_vo.created_at)
                })

    return repository_pb2.RepositoryInfo(**info)


def RepositoriesInfo(repo_vos, total_count, **kwargs):
    return repository_pb2.RepositoriesInfo(results=list(
        map(functools.partial(RepositoryInfo, **kwargs), repo_vos)), total_count=total_count)
