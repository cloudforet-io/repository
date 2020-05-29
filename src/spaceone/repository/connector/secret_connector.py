import logging

from spaceone.core.connector import BaseConnector
from spaceone.core import pygrpc
from spaceone.core.utils import parse_endpoint
from spaceone.core.error import *

__all__ = ['SecretConnector']

_LOGGER = logging.getLogger(__name__)


class SecretConnector(BaseConnector):
    def __init__(self, transaction, config, **kwargs):
        super().__init__(transaction, config, **kwargs)

        if 'endpoint' not in self.config:
            raise ERROR_WRONG_CONFIGURATION(key='endpoint')

        if len(self.config['endpoint']) > 1:
            raise ERROR_WRONG_CONFIGURATION(key='too many endpoint')

        for (k, v) in self.config['endpoint'].items():
            e = parse_endpoint(v)
            self.client = pygrpc.client(endpoint=f'{e.get("hostname")}:{e.get("port")}', version=k)
        # metadata may be escalated

        self.escalated_meta = self._get_escalated_meta()

    def get_secret(self, secret_id, domain_id):
        return self.client.Secret.get({'secret_id': secret_id, 'domain_id': domain_id},
                                      metadata=self.escalated_meta)

    def get_(self, secret_group_id, domain_id):
        return self.client.SecretGroup.get({'secret_group_id': secret_group_id, 'domain_id': domain_id},
                                           metadata=self.escalated_meta)

    def get_secret_data(self, secret_id, domain_id):
        return self.client.Secret.get_data({'secret_id': secret_id, 'domain_id': domain_id},
                                           metadata=self.escalated_meta)

    def _get_escalated_meta(self):
        meta = self.transaction.get_connection_meta()
        # _LOGGER.debug(f'[_get_escalated_meta] meta: {meta}')
        result = []
        for (k, v) in meta:
            if k == 'token' and hasattr(self, 'token') and self.token is not None:
                result.append((k, self.token))
            elif k == 'domain_id' and hasattr(self, 'domain_id') and self.domain_id is not None:
                result.append((k, self.domain_id))
            else:
                result.append((k, v))
        # _LOGGER.debug(f'[_get_escalated_meta] new_meta: {result}')
        return result
