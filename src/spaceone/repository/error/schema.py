from spaceone.core.error import *


class ERROR_NO_SCHEMA(ERROR_BASE):
    _message = 'Schema does not exists. (name = {name})'


class ERROR_INVALID_SCHEMA(ERROR_INVALID_ARGUMENT):
    _message = 'Schema format(JSON SCHEMA) is invalid. (key = {key})'
