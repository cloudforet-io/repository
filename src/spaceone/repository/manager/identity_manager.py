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
