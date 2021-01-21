import functools
from spaceone.api.core.v1 import tag_pb2
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
            'labels': schema_vo.labels,
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in schema_vo.tags],
            'project_id': schema_vo.project_id,
            'domain_id': schema_vo.domain_id,
            'created_at': change_timestamp_type(schema_vo.created_at),
            'updated_at': change_timestamp_type(schema_vo.updated_at)
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
