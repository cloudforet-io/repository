from spaceone.core.error import *


class ERROR_NO_PLUGIN(ERROR_BASE):
    _message = 'Plugin does not exists. (plugin_id = {plugin_id})'

class ERROR_INVALID_IMAGE_FORMAT(ERROR_BASE):
    _message = 'Image format is <repository name>/<image name> in {name}'

class ERROR_INVALID_IMAGE_NAME_FORMAT(ERROR_BASE):
    _message = 'Image name format is [a-zA-Z0-9\-]+ in {name}'

class ERROR_INVALID_IMAGE_LENGTH(ERROR_BASE):
    _message = 'The length of image should be less than equal {length} in {name}'

class ERROR_INVALID_TEMPLATE_SCHEMA(ERROR_INVALID_ARGUMENT):
    _message = 'Template schema format(JSON SCHEMA) is invalid. (key = {key})'
