from spaceone.core.manager import BaseManager


class IdentityManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity_connector = self.locator.get_connector('SpaceConnector', service='identity')

    def get_project(self, project_id, domain_id):
        return self.identity_connector.Project.get({'project_id': project_id, 'domain_id': domain_id})

    def list_projects(self, query, domain_id):
        return self.identity_connector.Project.list({'query': query, 'domain_id': domain_id})
