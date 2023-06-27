import functools
from spaceone.api.repository.v1 import policy_pb2, repository_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils

__all__ = ['PolicyInfo', 'PoliciesInfo']


def PolicyInfo(policy_info, minimal=False):
    info = {
        'policy_id': policy_info.get('policy_id'),
        'name': policy_info.get('name'),
    }

    if not minimal:
        info.update({
            'state': policy_info.get('state'),
            'permissions': change_list_value_type(policy_info.get('permissions')),
            'tags': change_struct_type(policy_info.get('tags')),
            'labels': change_list_value_type(policy_info.get('labels')),
            'project_id': policy_info.get('project_id'),
            'domain_id': policy_info.get('domain_id'),
            'created_at': utils.datetime_to_iso8601(policy_info.get('created_at')),
            'updated_at': utils.datetime_to_iso8601(policy_info.get('updated_at'))
        })

        if repository_info := policy_info.get('repository_info'):
            info.update({
                'repository_info': repository_pb2.RepositoryInfo(
                    repository_id=repository_info.get('repository_id'),
                    name=repository_info.get('name'),
                    repository_type=repository_info.get('repository_type'),
                )
            })

    return policy_pb2.PolicyInfo(**info)


def PoliciesInfo(policies_info, total_count, **kwargs):
    return policy_pb2.PoliciesInfo(results=list(
        map(functools.partial(PolicyInfo, **kwargs), policies_info)), total_count=total_count)
