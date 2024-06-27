import logging

from spaceone.repository.model.dashboard_template_model import DashboardTemplate
from spaceone.repository.manager.dashboard_template_manager import DashboardTemplateManager
from spaceone.repository.manager.repository_manager import RepositoryManager

__all__ = ["LocalDashboardTemplateManager"]

_LOGGER = logging.getLogger(__name__)


class LocalDashboardTemplateManager(DashboardTemplateManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_model: DashboardTemplate = self.locator.get_model("DashboardTemplate")
        self.repo_info = RepositoryManager.get_repositories(repository_type="LOCAL")[0]

    def create_template(self, params: dict):
        def _rollback(vo: DashboardTemplate):
            vo.delete()

        template_vo: DashboardTemplate = self.template_model.create(params)
        self.transaction.add_rollback(_rollback, template_vo)

        template_info = template_vo.to_dict()
        return self.change_response(template_info, self.repo_info)

    def update_template(self, params):
        template_vo = self.template_model.get(
            template_id=params["template_id"], domain_id=params["domain_id"]
        )
        return self.update_template_by_vo(params, template_vo)

    def enable_template(self, template_id, domain_id):
        template_vo = self.template_model.get(template_id=template_id, domain_id=domain_id)
        return self.update_template_by_vo({"state": "ENABLED"}, template_vo)

    def disable_template(self, template_id, domain_id):
        template_vo = self.template_model.get(template_id=template_id, domain_id=domain_id)
        return self.update_template_by_vo({"state": "DISABLED"}, template_vo)

    def update_template_by_vo(self, params, template_vo):
        def _rollback(old_data):
            _LOGGER.info(
                f'[ROLLBACK] Revert DashboardTemplate Data : {old_data["name"]} ({old_data["template_id"]})'
            )
            template_vo.update(old_data)

        self.transaction.add_rollback(_rollback, template_vo.to_dict())
        template_vo = template_vo.update(params)
        template_info = template_vo.to_dict()
        return self.change_response(template_info, self.repo_info)

    def delete_template(self, template_id, domain_id):
        template_vo = self.template_model.get(template_id=template_id, domain_id=domain_id)
        template_vo.delete()

    def get_template(self, repo_info: dict, template_id, domain_id: str):
        template_vo = self.template_model.get(template_id=template_id, domain_id=domain_id)

        template_info = template_vo.to_dict()
        return self.change_response(template_info, self.repo_info)

    def list_templates(self, repos_info: dict, query: dict, params: dict):
        domain_id = params.get("domain_id")
        keyword = query.get("keyword")
        query_filter = query.get("filter", [])
        query_filter_or = query.get("filter_or", [])
        query["filter"] = self._append_domain_filter(query_filter, domain_id)
        query["filter_or"] = self._append_keyword_filter(query_filter_or, keyword)
        if "repository" in query.get("only", []):
            query["only"].remove("repository")

        template_vos, total_count = self.template_model.query(**query)
        results = []
        for template_vo in template_vos:
            template_info = template_vo.to_dict()
            results.append(self.change_response(template_info, repos_info))

        return results, total_count

    @staticmethod
    def _append_domain_filter(query_filter, domain_id=None):
        if domain_id:
            query_filter.append({"k": "domain_id", "v": domain_id, "o": "eq"})

        return query_filter

    @staticmethod
    def _append_keyword_filter(query_filter_or, keyword):
        if keyword:
            query_filter_or.append({"k": "name", "v": keyword, "o": "contain"})

        return query_filter_or
