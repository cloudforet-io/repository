import logging

from spaceone.core import config
from spaceone.repository.error import *
from spaceone.repository.model.plugin_model import Plugin
from spaceone.repository.manager.plugin_manager import PluginManager
from spaceone.repository.manager.repository_manager import RepositoryManager

__all__ = ["LocalPluginManager"]

_LOGGER = logging.getLogger(__name__)
_REGISTRY_CONNECTOR_MAP = {
    "DOCKER_HUB": "DockerHubConnector",
    "AWS_PRIVATE_ECR": "AWSPrivateECRConnector",
    "HARBOR": "HarborConnector",
    "GITHUB": "GithubContainerRegistryConnector",
}


class LocalPluginManager(PluginManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_model: Plugin = self.locator.get_model("Plugin")
        self.repo_info = RepositoryManager.get_repositories(repository_type="LOCAL")[0]

    def create_plugin(self, params: dict):
        def _rollback(vo: Plugin):
            vo.delete()

        plugin_vo: Plugin = self.plugin_model.create(params)
        self.transaction.add_rollback(_rollback, plugin_vo)

        versions = self.get_plugin_versions(
            self.repo_info, plugin_vo.plugin_id, plugin_vo.domain_id
        )

        if len(versions) == 0:
            raise ERROR_NO_IMAGE_IN_REGISTRY(
                registry_type=plugin_vo.registry_type, image=plugin_vo.image
            )

        plugin_info = plugin_vo.to_dict()
        return self.change_response(plugin_info, self.repo_info)

    def update_plugin(self, params):
        plugin_vo = self.plugin_model.get(
            plugin_id=params["plugin_id"], domain_id=params["domain_id"]
        )
        return self.update_plugin_by_vo(params, plugin_vo)

    def enable_plugin(self, plugin_id, domain_id):
        plugin_vo = self.plugin_model.get(plugin_id=plugin_id, domain_id=domain_id)
        return self.update_plugin_by_vo({"state": "ENABLED"}, plugin_vo)

    def disable_plugin(self, plugin_id, domain_id):
        plugin_vo = self.plugin_model.get(plugin_id=plugin_id, domain_id=domain_id)
        return self.update_plugin_by_vo({"state": "DISABLED"}, plugin_vo)

    def update_plugin_by_vo(self, params, plugin_vo):
        def _rollback(old_data):
            _LOGGER.info(
                f'[ROLLBACK] Revert Plugin Data : {old_data["name"]} ({old_data["plugin_id"]})'
            )
            plugin_vo.update(old_data)

        self.transaction.add_rollback(_rollback, plugin_vo.to_dict())
        plugin_vo = plugin_vo.update(params)
        plugin_info = plugin_vo.to_dict()
        return self.change_response(plugin_info, self.repo_info)

    def delete_plugin(self, plugin_id, domain_id):
        plugin_vo = self.plugin_model.get(plugin_id=plugin_id, domain_id=domain_id)
        plugin_vo.delete()

    def get_plugin(self, repo_info: dict, plugin_id, domain_id: str):
        plugin_vo = self.plugin_model.get(plugin_id=plugin_id, domain_id=domain_id)

        plugin_info = plugin_vo.to_dict()
        return self.change_response(plugin_info, self.repo_info)

    def list_plugins(self, repos_info: dict, query: dict, params: dict):
        domain_id = params.get("domain_id")
        keyword = query.get("keyword")
        query_filter = query.get("filter", [])
        query_filter_or = query.get("filter_or", [])
        query["filter"] = self._append_domain_filter(query_filter, domain_id)
        query["filter_or"] = self._append_keyword_filter(query_filter_or, keyword)
        if "repository" in query.get("only", []):
            query["only"].remove("repository")

        plugin_vos, total_count = self.plugin_model.query(**query)
        results = []
        for plugin_vo in plugin_vos:
            plugin_info = plugin_vo.to_dict()
            results.append(self.change_response(plugin_info, repos_info))

        return results, total_count

    def get_plugin_versions(self, repo_info: dict, plugin_id: str, domain_id: str):
        plugin_vo = self.plugin_model.get(plugin_id=plugin_id, domain_id=domain_id)

        registry_url = (
            config.get_global("REGISTRY_INFO", {})
            .get(plugin_vo.registry_type)
            .get("url")
        )
        registry_connector = _REGISTRY_CONNECTOR_MAP[plugin_vo.registry_type]

        try:
            connector = self.locator.get_connector(registry_connector)
            tags = connector.get_tags(registry_url, plugin_vo.image)
        except Exception as e:
            _LOGGER.error(f"[get_plugin_versions] get_tags error: {e}", exc_info=True)
            raise e
        else:
            return tags

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
