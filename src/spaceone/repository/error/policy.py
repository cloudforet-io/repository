from spaceone.core.error import *


class ERROR_NO_POLICY(ERROR_INVALID_ARGUMENT):
    _message = 'Policy does not exists. (policy_id = {policy_id})'


class ERROR_INVALID_POLICY_ID_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = 'Wrong policy id. Only lower-case/number/hyphen character can be used. (policy_id = {policy_id})'


class ERROR_INVALID_POLICY_ID_LENGTH(ERROR_INVALID_ARGUMENT):
    _message = 'The length of policy_id should be less than equal {length} in {policy_id}'

class ERROR_SORT_KEY(ERROR_INVALID_ARGUMENT):
    _message = 'Sort key is invalid. (sort_key = {sort_key})'
