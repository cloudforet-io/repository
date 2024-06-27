import logging

from spaceone.core.connector.space_connector import SpaceConnector

from spaceone.repository.manager.dashboard_template_manager import DashboardTemplateManager

__all__ = ["RemoteDashboardTemplateManager"]

_LOGGER = logging.getLogger(__name__)


class RemoteDashboardTemplateManager(DashboardTemplateManager):
    def get_template(self, repo_info: dict, template_id: str, domain_id: str = None):
        endpoint = repo_info["endpoint"]
        market_place_token = repo_info["token"]

        remote_repo_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint, token=market_place_token
        )

        template_info: dict = remote_repo_conn.dispatch(
            "DashboardTemplate.get", {"template_id": template_id, "repository_id": "repo-local"}
        )

        return self.change_response(template_info, repo_info)

    def list_templates(self, repo_info: dict, query: dict, params: dict):
        try:
            endpoint = repo_info["endpoint"]
            market_place_token = repo_info["token"]

            _LOGGER.debug(f"[list_templates] Remote Repository endpoint: {endpoint}")

            remote_repo_conn: SpaceConnector = self.locator.get_connector(
                SpaceConnector, endpoint=endpoint, token=market_place_token
            )

            response = remote_repo_conn.dispatch(
                "DashboardTemplate.list", {"query": query, "repository_id": "repo-local"}
            )

            plugins_info = response.get("results", [])
            total_count = response.get("total_count", 0)
            results = []

            for template_info in plugins_info:
                results.append(self.change_response(template_info, repo_info))

            return results, total_count
        except Exception as e:
            _LOGGER.error(f"[list_templates] {e}")
            return [], 0
