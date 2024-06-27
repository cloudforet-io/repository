import logging
from abc import abstractmethod

from spaceone.core.manager import BaseManager

__all__ = ["DashboardTemplateManager"]
_LOGGER = logging.getLogger(__name__)


class DashboardTemplateManager(BaseManager):
    def create_template(self, params):
        pass

    def update_template(self, params):
        pass

    def enable_template(self, template_id, domain_id):
        pass

    def disable_template(self, template_id, domain_id):
        pass

    def delete_template(self, template_id, domain_id):
        pass

    @abstractmethod
    def get_template(self, repo_info: dict, template_id, domain_id):
        pass

    @abstractmethod
    def list_templates(self, repo_info: dict, query: dict, params: dict):
        pass

    @staticmethod
    def change_response(
            info: dict, repo_info: dict = None
    ) -> dict:
        if repo_info:
            info["repository_info"] = {
                "repository_id": repo_info["repository_id"],
                "name": repo_info["name"],
                "repository_type": repo_info["repository_type"],
            }

        return info
