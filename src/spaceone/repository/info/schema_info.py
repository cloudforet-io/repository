import functools
from spaceone.api.repository.v1 import schema_pb2
from spaceone.core.pygrpc.message_type import *
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
            'tags': change_struct_type(schema_vo.tags),
            'project_id': schema_vo.project_id,
            'domain_id': schema_vo.domain_id,
            'created_at': change_timestamp_type(schema_vo.created_at)
            })
        # WARNING
        # Based on local_schema or remote_schema
        # vo has different repository or repository_info field
        if getattr(schema_vo, 'repository', None) is not None:
            info.update({
                'repository_info': RepositoryInfo(schema_vo.repository, minimal=True)})
        if getattr(schema_vo, 'repository_info', None) is not None:
            info.update({
                'repository_info': RepositoryInfo(schema_vo.repository_info, minimal=True)})

    return schema_pb2.SchemaInfo(**info)


def SchemasInfo(schema_vos, total_count):
    results = list(map(functools.partial(SchemaInfo), schema_vos))
    return schema_pb2.SchemasInfo(results=results, total_count=total_count)
