import logging

from spaceone.core.error import *

from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.repository.error import *
from spaceone.repository.manager.repository_manager import RepositoryManager

_LOGGER = logging.getLogger(__name__)


class RemoteRepositoryManager(RepositoryManager):

    def register_repository(self, params):
        endpoint = params.get('endpoint')

        if endpoint is None:
            raise ERROR_REQUIRED_PARAMETER(key='endpoint')

        remote_repo_vos = self.filter_repositories(repository_type="remote", endpoint=endpoint)
        if remote_repo_vos.count() > 0:
            raise ERROR_REMOTE_REPOSITORY_ALREADY_EXIST(endpoint=endpoint)

        remote_repo_conn: SpaceConnector = self.locator.get_connector('SpaceConnector', endpoint=endpoint)
        response = remote_repo_conn.dispatch('Repository.list', {'repository_type': 'local'})
        total_count = response.get('total_count', 0)

        if total_count == 0:
            raise ERRROR_NOT_SET_UP_REMOTE_REPOSITORY()

        remote_repo_info = response['results'][0]

        # Overwrite repository_id to Remote one
        params['repository_id'] = remote_repo_info['repository_id']
        params['order'] = 2

        return self.repo_model.create(params)
