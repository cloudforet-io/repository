import copy
import logging
import re

from spaceone.core.service import *
from spaceone.core import config, utils

from spaceone.repository.error import *
from spaceone.repository.manager.dashboard_template_manager.local_dashboard_template_manager import (
    LocalDashboardTemplateManager,
)
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class DashboardTemplateService(BaseService):
    resource = "DashboardTemplate"

    @transaction(permission="repository:DashboardTemplate.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["name", "domain_id"])
    def register(self, params):
        """Register DashboardTemplate (local repo only)

        Args:
            params (dict): {
                'template_id': 'str',
                'name': 'str',              # required
                'template_type': 'str',
                'dashboards': 'str',
                'labels': 'list',
                'tags': 'dict',
                'domain_id': 'str'          # injected from auth
            }

        Returns:
            template_info (dict)
        """

        template_id = params.get("template_id")

        if template_id is None:
            template_id = utils.generate_id("template")

        template_mgr: LocalDashboardTemplateManager = self.locator.get_manager("LocalDashboardTemplateManager")

        # Only LOCAL repository can be registered
        repo_mgr: RepositoryManager = self.locator.get_manager("RepositoryManager")
        params["template_id"] = template_id
        params["repository"] = repo_mgr.get_local_repository()
        params["repository_id"] = params["repository"].get("repository_id")

        return template_mgr.create_template(params)

    @transaction(permission="repository:DashboardTemplate.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["template_id", "domain_id"])
    def update(self, params):
        """Update DashboardTemplate. (local repo only)

        Args:
            params (dict): {
                'template_id': 'str',     # required
                'name': 'str',
                'template_type': 'str',
                'dashboards': 'str',
                'labels': 'list',
                'tags': 'dict'
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            template_info (dict)
        """

        template_mgr: LocalDashboardTemplateManager = self.locator.get_manager("LocalDashboardTemplateManager")
        return template_mgr.update_template(params)

    @transaction(
        permission="repository:DashboardTemplate.write",
        role_types=["DOMAIN_ADMIN"],
    )
    @check_required(["template_id", "domain_id"])
    def enable(self, params):
        """Enable template (local repo only)

        Args:
            params (dict): {
                'template_id': 'str',     # required
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            template_info (dict)
        """

        template_mgr: LocalDashboardTemplateManager = self.locator.get_manager("LocalDashboardTemplateManager")
        return template_mgr.enable_template(params["template_id"], params["domain_id"])

    @transaction(
        permission="repository:DashboardTemplate.write",
        role_types=["DOMAIN_ADMIN"],
    )
    @check_required(["template_id", "domain_id"])
    def disable(self, params):
        """Disable DashboardTemplate (local repo only)

        Args:
            params (dict): {
                'template_id': 'str',     # required
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            template_info (dict)
        """
        template_mgr: LocalDashboardTemplateManager = self.locator.get_manager("LocalDashboardTemplateManager")
        return template_mgr.disable_template(params["template_id"], params["domain_id"])

    @transaction(permission="repository:DashboardTemplate.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["template_id", "domain_id"])
    def deregister(self, params):
        """Deregister DashboardTemplate (local repo only)

        Args:
            params (dict): {
                'template_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        template_mgr: LocalDashboardTemplateManager = self.locator.get_manager("LocalDashboardTemplateManager")
        return template_mgr.delete_template(params["template_id"], params["domain_id"])

    @transaction(
        permission="repository:DashboardTemplate.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "USER"],
    )
    @check_required(["template_id"])
    @change_only_key({"repository_info": "repository"})
    def get(self, params):
        """Get DashboardTemplate (all repositories)

        Args:
            params (dict): {
                'template_id': 'str',       # required
                'repository_id': 'str',
                'domain_id': 'str',         # injected from auth (optional)
            }

        Returns:
            template_info (dict)
        """

        template_id = params["template_id"]
        repo_id = params.get("repository_id")
        domain_id = params.get("domain_id")

        repo_mgr: RepositoryManager = self.locator.get_manager("RepositoryManager")
        repos_info = repo_mgr.get_repositories(repo_id)
        for repo_info in repos_info:
            _LOGGER.debug(
                f"[get] find at name: {repo_info['name']} "
                f"(repo_type: {repo_info['repository_type']})"
            )

            template_mgr = self._get_template_manager_by_repo(repo_info["repository_type"])
            try:
                return template_mgr.get_template(repo_info, template_id, domain_id)
            except Exception as e:
                _LOGGER.debug(
                    f"[get] Can not find template({template_id}) at {repo_info['name']}"
                )

        raise ERROR_NO_DASHBOARD_TEMPLATE(template_id=template_id)

    @transaction(
        permission="repository:DashboardTemplate.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "USER"],
    )
    @change_only_key({"repository_info": "repository"}, key_path="query.only")
    @append_query_filter(
        ["template_id", "name", "state", "dashboard_type"]
    )
    def list(self, params):
        """List templates (all repositories)

        Args:
            params (dict): {
                'repository_id': 'str',
                'template_id': 'str',
                'name': 'str',
                'state': 'str',
                'dashboard_type': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of template_info'
            total_count (int)
        """

        query = params.get("query", {})
        query["only"] = query.get("only", [])

        repo_mgr: RepositoryManager = self.locator.get_manager("RepositoryManager")
        if repository_id := params.get("repository_id"):
            repo_info = repo_mgr.get_repository(repository_id)
            template_mgr = self._get_template_manager_by_repo(repo_info["repository_type"])

            return template_mgr.list_templates(repo_info, query, params)
        else:
            all_templates_info = []
            template_total_count = 0
            query_page = None
            if "page" in query:
                query_page = query["page"]
                del query["page"]

            repos_info: list = repo_mgr.get_repositories()
            for repo_info in repos_info:
                template_mgr = self._get_template_manager_by_repo(
                    repo_info["repository_type"]
                )
                templates_info, total_count = template_mgr.list_templates(
                    repo_info, copy.deepcopy(query), params
                )
                all_templates_info += templates_info
                template_total_count += total_count

            if query_page:
                page_start = query_page.get("start", 1) - 1
                page_limit = query_page.get("limit")

                if page_limit:
                    all_templates_info = all_templates_info[
                        page_start : page_start + page_limit
                    ]

            return all_templates_info, template_total_count

    def _get_template_manager_by_repo(self, repository_type: str):
        if repository_type == "LOCAL":
            return self.locator.get_manager("LocalDashboardTemplateManager")
        elif repository_type == "MANAGED":
            return self.locator.get_manager("ManagedDashboardTemplateManager")
        else:
            return self.locator.get_manager("RemoteDashboardTemplateManager")
