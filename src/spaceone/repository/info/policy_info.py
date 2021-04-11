import functools
from google.protobuf.struct_pb2 import Struct
from spaceone.api.repository.v1 import policy_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.repository.model.policy_model import Policy
from spaceone.repository.info.repository_info import RepositoryInfo

__all__ = ['PolicyInfo', 'PoliciesInfo']


def PolicyInfo(policy_vo: Policy, minimal=False):
    info = {
        'policy_id': policy_vo.policy_id,
        'name': policy_vo.name
    }

    if not minimal:
        info.update({
            'permissions': change_list_value_type(policy_vo.permissions),
            'labels': change_list_value_type(policy_vo.labels),
            'tags': policy_vo.tags if isinstance(policy_vo.tags, Struct)
            else change_struct_type(utils.tags_to_dict(policy_vo.tags)),
            'project_id': policy_vo.project_id,
            'domain_id': policy_vo.domain_id,
            'created_at': utils.datetime_to_iso8601(policy_vo.created_at) or policy_vo.created_at,
            'updated_at': utils.datetime_to_iso8601(policy_vo.updated_at) or policy_vo.updated_at
            })
        # WARNING
        # Based on local_policy or remote_policy
        # vo has different repository or repository_info field
        if getattr(policy_vo, 'repository', None):
            info.update({
                'repository_info': RepositoryInfo(policy_vo.repository, minimal=True)})
        if getattr(policy_vo, 'repository_info', None):
            info.update({
                'repository_info': RepositoryInfo(policy_vo.repository_info, minimal=True)})

        # Temporary code for DB migration
        if not getattr(policy_vo, 'repository_id', None) and getattr(policy_vo, 'repository', None):
            policy_vo.update({'repository_id': policy_vo.repository.repository_id})

    return policy_pb2.PolicyInfo(**info)


def PoliciesInfo(policy_vos, total_count, **kwargs):
    return policy_pb2.PoliciesInfo(results=list(
        map(functools.partial(PolicyInfo, **kwargs), policy_vos)), total_count=total_count)
