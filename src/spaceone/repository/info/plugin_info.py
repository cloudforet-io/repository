import functools
from spaceone.api.repository.v1 import plugin_pb2
from spaceone.core import config
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.repository.model.plugin_model import Plugin
from spaceone.repository.info.repository_info import RepositoryInfo

__all__ = ['PluginInfo', 'PluginsInfo', 'VersionsInfo']


def PluginInfo(plugin_vo, minimal=False):
    info = {
        'plugin_id': plugin_vo.plugin_id,
        'name': plugin_vo.name,
        'state': plugin_vo.state,
        'image': plugin_vo.image,
        'service_type': plugin_vo.service_type,
        'registry_type': plugin_vo.registry_type,
        'provider': plugin_vo.provider
    }
    if not minimal:
        info.update({
            'registry_config': change_struct_type(plugin_vo.registry_config),
            'capability': change_struct_type(plugin_vo.capability),
            'template': change_struct_type(plugin_vo.template),
            'labels': change_list_value_type(plugin_vo.labels),
            'project_id': plugin_vo.project_id,
            'domain_id': plugin_vo.domain_id,
            'created_at': utils.datetime_to_iso8601(plugin_vo.created_at) or plugin_vo.created_at,
            'updated_at': utils.datetime_to_iso8601(plugin_vo.updated_at) or plugin_vo.updated_at
            })

        if isinstance(plugin_vo, plugin_pb2.PluginInfo):
            info['tags'] = plugin_vo.tags
            info['registry_url'] = plugin_vo.registry_url
        else:
            info['tags'] = change_struct_type(utils.tags_to_dict(plugin_vo.tags))
            if plugin_vo.registry_type:
                info['registry_url'] = config.get_global('REGISTRY_URL_MAP', {}).get(plugin_vo.registry_type)

        # WARNING
        # Based on local_plugin or remote_plugin
        # vo has different repository or repository_info field
        if getattr(plugin_vo, 'repository', None):
            info.update({
                'repository_info': RepositoryInfo(plugin_vo.repository, minimal=True)})
        if getattr(plugin_vo, 'repository_info', None):
            info.update({
                'repository_info': RepositoryInfo(plugin_vo.repository_info, minimal=True)})

    return plugin_pb2.PluginInfo(**info)


def PluginsInfo(plugin_vos, total_count, **kwargs):
    return plugin_pb2.PluginsInfo(results=list(
        map(functools.partial(PluginInfo, **kwargs), plugin_vos)), total_count=total_count)


def VersionsInfo(version_list):
    return plugin_pb2.VersionsInfo(results=version_list, total_count=len(version_list))
