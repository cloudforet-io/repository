import logging

from google.protobuf.json_format import MessageToDict

from spaceone.core.connector import BaseConnector
from spaceone.core import pygrpc
from spaceone.core.utils import *
from spaceone.core.auth.jwt.jwt_util import JWTUtil
from spaceone.repository.error import *

__all__ = ["RepositoryConnector"]

_LOGGER = logging.getLogger(__name__)


class RepositoryConnector(BaseConnector):
    client = None

    def __init__(self, transaction, config, **kwargs):
        super().__init__(transaction, config, **kwargs)

        """ Overwrite configuration

        Remote Repository has diffrent authentication.
        So do not use your token at meta.
        Use another authentication algorithm like token

        Args:
            connn: dict (endpoint, version, ...)

        """
        #_LOGGER.debug("[RepositoryConnector] meta: %s" % self.transaction.meta)
        #_LOGGER.debug("[RepositoryConnector] self.conn: %s" % self.conn)

        e = parse_endpoint(self.conn['endpoint'])
        self.protocol = e['scheme']
        if self.protocol == 'grpc':
            self.client = pygrpc.client(endpoint="%s:%s" % (e['hostname'], e['port']), version=self.conn['version'])
        elif self.protocol == 'http':
            # TODO: implement
            raise ERROR_UNSUPPORTED_API(message=self.protocol)

        # Update meta (like domain_id)
        # TODO: change meta to marketplace token
        meta = self.transaction.get_connection_meta()
        new_meta = []
        if 'credential' in self.conn:
            credential = self.conn['credential']
            if 'token' in credential:
                # self.meta = [('token',credential['token'])]
                self._token = credential['token']
            else:
                # TODO: raise ERROR
                raise ERROR_CONFIGURATION(key='credential')

            for (k, v) in meta:
                if k != 'token' and v is not None:
                    new_meta.append((k, v))
                elif k == 'token':
                    new_meta.append(('token', self._token))
            self.meta = new_meta

        # Update domain_id
        # This repository is not our domain.
        # find domain_id from token
        decoded_token = JWTUtil.unverified_decode(self._token)
        self.domain_id = decoded_token['did']

    def get_local_repository(self, domain_id):
        """ Repository.list
        Get Repository Information of Remote
        Return only 1 Repository
        """
        param = {'repository_type': 'local', 'domain_id': domain_id}
        response = self.client.Repository.list(param, metadata=self.meta)
        # _LOGGER.debug(f'[get_local_repository] Repositories: {repositories}')
        # _LOGGER.debug(f'[get_local_repository] count: {count}')
        # if count > 1:
        #    for repo in repositories:
        #        _LOGGER.debug(f'[get_repository] name: {repo.name}')
        return response.results[0]

    def get_policy(self, policy_id, only=None):
        """ get policy from repository
        API: repository.Policy.get
        """
        param = {'policy_id': policy_id, 'domain_id': self.domain_id, 'only': only}
        _LOGGER.debug("param: %s" % param)
        return self.client.Policy.get(param, metadata=self.meta)

    def list_policies(self, query):
        _LOGGER.debug(f'[list_policies] query: {query}')
        repo_id = self._get_repo_id_from_query(query)
        # query contains domain_id (my domain_id),
        # but we needs remote_repository's domain_id
        # remove domain_id at query
        updated_query = self._remove_domain_id_from_query(query)
        params = {
            'repository_id': repo_id,
            'domain_id': self.domain_id,
            'query': updated_query
        }
        _LOGGER.debug("params: %s" % params)
        return self.client.Policy.list(params, metadata=self.meta)

    def get_schema(self, name, only=None):
        """ get schema from repository
        API: repository.Schema.get
        """
        param = {'name': name, 'domain_id': self.domain_id, 'only': only}
        _LOGGER.debug("param: %s" % param)
        return self.client.Schema.get(param, metadata=self.meta)

    def list_schemas(self, query):
        _LOGGER.debug(f'[list_schemas] query: {query}')
        repo_id = self._get_repo_id_from_query(query)
        # query contains domain_id (my domain_id),
        # but we needs remote_repository's domain_id
        # remove domain_id at query
        updated_query = self._remove_domain_id_from_query(query)
        params = {
            'repository_id': repo_id,
            'domain_id': self.domain_id,
            'query': updated_query
        }
        _LOGGER.debug("params: %s" % params)
        return self.client.Schema.list(params, metadata=self.meta)

    def get_plugin(self, plugin_id, only=None):
        """ get plugin from repository
        API: repository.Plugin.get
        """
        param = {'plugin_id': plugin_id, 'domain_id': self.domain_id, 'only': only}
        _LOGGER.debug("param: %s" % param)
        return self.client.Plugin.get(param, metadata=self.meta)

    def list_plugins(self, query):
        _LOGGER.debug(f'[list_plugins] query: {query}')
        repo_id = self._get_repo_id_from_query(query)
        # query contains domain_id (my domain_id),
        # but we needs remote_repository's domain_id
        # remove domain_id at query
        updated_query = self._remove_domain_id_from_query(query)
        params = {
            'repository_id': repo_id,
            'domain_id': self.domain_id,
            'query': updated_query
        }
        _LOGGER.debug("params: %s" % params)
        return self.client.Plugin.list(params, metadata=self.meta)

    def get_plugin_version(self, plugin_id):
        param = {'plugin_id': plugin_id, 'domain_id': self.domain_id}
        _LOGGER.debug("[RepositoryConnector] call get_plugin_versions")
        res = self.client.Plugin.get_versions(param, metadata=self.meta)
        # Convert to list
        _LOGGER.debug(f'[get_plugin_version] {res}')
        result_dict = MessageToDict(res)
        if 'results' in result_dict:
            result = result_dict['results']
        elif 'version' in result_dict:
            result = result_dict['version']
        else:
            _LOGGER.error(f'[get_plugin_version] version: {result_dict}')
            result = None

        if len(result) == 0:
            result = None
        _LOGGER.debug(f'[get_plugin_version] result: {result}')
        return result

    ############
    # Internal
    ############
    def _get_repo_id_from_query(self, query):
        """ get repository_id

        Assume


        query example)
        query = {'filter': [{'k':'repository_id', 'v':'repo-xxx', 'o':'eq'}]
        query = {'filter': [{'key':'repository_id', 'value':'repo-xxx', 'operator':'eq'}]
        """
        v = query['filter']
        for item in v:
            if 'k' in item and item['k'] == 'repository_id':
                return item['v']
            elif 'key' in item and item['key'] == 'repository_id':
                return item['value']

    def _remove_domain_id_from_query(self, query):
        """
        query = {'page': {'start': 1.0, 'limit': 2.0}}

        Remove domain_id at filter
        Update page to int value (may be float)
        """

        new_query = query.copy()

        # Warning: wrong transfer of query
        # page
        page = new_query.get('page', {})
        page_dic = {}
        for k, v in page.items():
            page_dic[k] = int(v)
        if page_dic != {}:
            new_query['page'] = page_dic

        v = new_query['filter']
        for index in range(len(v)):
            item = v[index]
            if 'k' in item and item['k'] == 'domain_id':
                del new_query['filter'][index]
                break
            elif 'key' in item and item['key'] == 'domain_id':
                del new_query['filter'][index]
                break
        return new_query
