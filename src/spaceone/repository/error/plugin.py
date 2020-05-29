from spaceone.core.error import *


class ERROR_NO_PLUGIN(ERROR_BASE):
    _message = 'Plugin: {plugin_id} does not exists.'


class ERROR_INVALID_TEMPLATE_SCHEMA(ERROR_INVALID_ARGUMENT):
    _message = 'Template schema format(JSON SCHEMA) is invalid. (key = {key})'
