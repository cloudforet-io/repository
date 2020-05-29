from spaceone.core.manager import BaseManager
from spaceone.repository.connector.identity_connector import IdentityConnector


class IdentityManager(BaseManager):

    def get_project(self, project_id, domain_id):
        identity_conn: IdentityConnector = self.locator.get_connector('IdentityConnector')
        return identity_conn.get_project(project_id, domain_id)

    def list_projects(self, query, domain_id):
        identity_conn: IdentityConnector = self.locator.get_connector('IdentityConnector')
        return identity_conn.list_projects(query, domain_id)
