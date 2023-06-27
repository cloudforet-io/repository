import functools
from spaceone.api.repository.v1 import schema_pb2, repository_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils

__all__ = ['SchemaInfo', 'SchemasInfo']


def SchemaInfo(schema_info: dict, minimal=False):
    info = {
        'name': schema_info.get('name'),
        'service_type': schema_info.get('service_type'),
    }

    if not minimal:
        info.update({
            'schema': change_struct_type(schema_info.get('schema')),
            'tags': change_struct_type(schema_info.get('tags')),
            'labels': change_list_value_type(schema_info.get('labels')),
            'project_id': schema_info.get('project_id'),
            'domain_id': schema_info.get('domain_id'),
            'created_at': utils.datetime_to_iso8601(schema_info.get('created_at')),
            'updated_at': utils.datetime_to_iso8601(schema_info.get('updated_at'))
            })

        if repository_info := schema_info.get('repository_info'):
            info.update({
                'repository_info': repository_pb2.RepositoryInfo(
                    repository_id=repository_info.get('repository_id'),
                    name=repository_info.get('name'),
                    repository_type=repository_info.get('repository_type'),
                )
            })

    return schema_pb2.SchemaInfo(**info)


def SchemasInfo(schemas_info, total_count, **kwargs):
    return schema_pb2.SchemasInfo(results=list(
        map(functools.partial(SchemaInfo, **kwargs), schemas_info)), total_count=total_count)
