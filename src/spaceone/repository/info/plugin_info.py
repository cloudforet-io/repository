import functools
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.repository.v1 import plugin_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.repository.model.plugin_model import Plugin
from spaceone.repository.info.repository_info import RepositoryInfo

__all__ = ['PluginInfo', 'PluginsInfo', 'VersionsInfo']


def PluginInfo(plugin_vo: Plugin, minimal=False):
    info = {
        'plugin_id': plugin_vo.plugin_id,
        'name': plugin_vo.name,
        'state': plugin_vo.state,
        'image': plugin_vo.image,
        'service_type': plugin_vo.service_type,
        'provider': plugin_vo.provider
    }
    if not minimal:
        info.update({
            'registry_url': plugin_vo.registry_url,
            'capability': change_struct_type(plugin_vo.capability),
            'template': change_struct_type(plugin_vo.template),
            'labels': plugin_vo.labels,
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in plugin_vo.tags],
            'project_id': plugin_vo.project_id,
            'domain_id': plugin_vo.domain_id,
            'created_at': change_timestamp_type(plugin_vo.created_at),
            'updated_at': change_timestamp_type(plugin_vo.updated_at)
            })
        # WARNING
        # Based on local_plugin or remote_plugin
        # vo has different repository or repository_info field
        if getattr(plugin_vo, 'repository', None):
            info.update({
                'repository_info': RepositoryInfo(plugin_vo.repository, minimal=True)})
        if getattr(plugin_vo, 'repository_info', None):
            info.update({
                'repository_info': RepositoryInfo(plugin_vo.repository_info, minimal=True)})

        # Temporary code for DB migration
        if not getattr(plugin_vo, 'repository_id', None) and getattr(plugin_vo, 'repository', None):
            plugin_vo.update({'repository_id': plugin_vo.repository.repository_id})

    return plugin_pb2.PluginInfo(**info)


def PluginsInfo(plugin_vos, total_count, **kwargs):
    return plugin_pb2.PluginsInfo(results=list(
        map(functools.partial(PluginInfo, **kwargs), plugin_vos)), total_count=total_count)


def VersionsInfo(version_list):
    return plugin_pb2.VersionsInfo(results=version_list, total_count=len(version_list))
