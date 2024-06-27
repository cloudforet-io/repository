import logging
from spaceone.repository.error import *
from spaceone.repository.manager.dashboard_template_manager import DashboardTemplateManager

__all__ = ["ManagedDashboardTemplateManager"]

_LOGGER = logging.getLogger(__name__)


class ManagedDashboardTemplateManager(DashboardTemplateManager):

    def get_template(self, repo_info: dict, template_id: str, domain_id: str):
        raise ERROR_NO_DASHBOARD_TEMPLATE(template_id=template_id)

    def list_templates(self, repo_info: dict, query: dict, params: dict):
        return [], 0
