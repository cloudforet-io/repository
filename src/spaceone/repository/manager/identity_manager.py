from spaceone.core import cache

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector


class IdentityManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='identity')

    def get_project(self, project_id, domain_id):
        return self.identity_connector.dispatch('Project.get', {'project_id': project_id, 'domain_id': domain_id})

    def list_projects(self, query, domain_id):
        return self.identity_connector.dispatch('Project.list', {'query': query, 'domain_id': domain_id})

    @cache.cacheable(key='domain_id.root', expire=3600)
    def get_root_domain_id(self, name="root"):
        response = self.identity_connector.dispatch('Domain.list', {'name': name, 'query': {'only': ['domain_id']}})
        if response['total_count'] == 1:
            for result in response['results']:
                return result['domain_id']
        return False
