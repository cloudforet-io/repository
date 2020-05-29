from spaceone.core.error import *


class ERROR_NO_SCHEMA(ERROR_BASE):
    _message = 'schema: {name} does not exists.'


class ERROR_INVALID_SCHEMA(ERROR_INVALID_ARGUMENT):
    _message = 'Schema format(JSON SCHEMA) is invalid. (key = {key})'
