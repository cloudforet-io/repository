import functools
from google.protobuf.struct_pb2 import Struct
from spaceone.api.repository.v1 import schema_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.repository.model.schema_model import Schema
from spaceone.repository.info.repository_info import RepositoryInfo

__all__ = ['SchemaInfo', 'SchemasInfo']


def SchemaInfo(schema_vo: Schema, minimal=False):
    info = {
        'name': schema_vo.name,
        'service_type': schema_vo.service_type
    }

    if not minimal:
        info.update({
            'schema': change_struct_type(schema_vo.schema),
            'labels': change_list_value_type(schema_vo.labels),
            'tags': schema_vo.tags if isinstance(schema_vo.tags, Struct)
            else change_struct_type(utils.tags_to_dict(schema_vo.tags)),
            'project_id': schema_vo.project_id,
            'domain_id': schema_vo.domain_id,
            'created_at': utils.datetime_to_iso8601(schema_vo.created_at) or schema_vo.created_at,
            'updated_at': utils.datetime_to_iso8601(schema_vo.updated_at) or schema_vo.updated_at
            })
        # WARNING
        # Based on local_schema or remote_schema
        # vo has different repository or repository_info field
        if getattr(schema_vo, 'repository', None):
            info.update({
                'repository_info': RepositoryInfo(schema_vo.repository, minimal=True)})
        if getattr(schema_vo, 'repository_info', None):
            info.update({
                'repository_info': RepositoryInfo(schema_vo.repository_info, minimal=True)})

        # Temporary code for DB migration
        if not getattr(schema_vo, 'repository_id', None) and getattr(schema_vo, 'repository', None):
            schema_vo.update({'repository_id': schema_vo.repository.repository_id})

    return schema_pb2.SchemaInfo(**info)


def SchemasInfo(schema_vos, total_count, **kwargs):
    return schema_pb2.SchemasInfo(results=list(
        map(functools.partial(SchemaInfo, **kwargs), schema_vos)), total_count=total_count)
