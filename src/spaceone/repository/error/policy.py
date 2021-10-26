from spaceone.core.error import *


class ERROR_NO_POLICY(ERROR_BASE):
    _message = 'Policy does not exists. (policy_id = {policy_id})'


class ERROR_INVALID_POLICY_ID_FORMAT(ERROR_BASE):
    _message = 'Wrong policy id. Only lower-case/number/hyphen character can be used. (policy_id = {policy_id})'

class ERROR_INVALID_POLICY_ID_LENGTH(ERROR_BASE):
    _message = 'The length of policy_id should be less than equal {length} in {policy_id}'