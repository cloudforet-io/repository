import functools
from spaceone.api.repository.v1 import dashboard_template_pb2, repository_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils

__all__ = ["DashboardTemplateInfo", "DashboardTemplatesInfo"]


def DashboardTemplateInfo(template_info: dict, minimal=False):
    info = {
        "template_id": template_info.get("template_id"),
        "name": template_info.get("name"),
        "state": template_info.get("state"),
        "template_type": template_info.get("template_type"),
    }

    if not minimal:
        info.update(
            {
                "dashboards": change_list_value_type(template_info.get("dashboards")),
                "tags": change_struct_type(template_info.get("tags")),
                "labels": change_list_value_type(template_info.get("labels")),
                "domain_id": template_info.get("domain_id"),
                "created_at": utils.datetime_to_iso8601(template_info.get("created_at")),
                "updated_at": utils.datetime_to_iso8601(template_info.get("updated_at")),
            }
        )

        if repository_info := template_info.get("repository_info"):
            info.update(
                {
                    "repository_info": repository_pb2.RepositoryInfo(
                        repository_id=repository_info.get("repository_id"),
                        name=repository_info.get("name"),
                        repository_type=repository_info.get("repository_type"),
                    )
                }
            )

    return dashboard_template_pb2.DashboardTemplateInfo(**info)


def DashboardTemplatesInfo(templates_info, total_count, **kwargs):
    return dashboard_template_pb2.DashboardTemplatesInfo(
        results=list(map(functools.partial(DashboardTemplateInfo, **kwargs), templates_info)),
        total_count=total_count,
    )
