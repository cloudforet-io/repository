from spaceone.core.error import *


class ERROR_NO_PLUGIN(ERROR_INVALID_ARGUMENT):
    _message = 'Plugin does not exists. (plugin_id = {plugin_id})'


class ERROR_INVALID_IMAGE_NAME_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = 'Image name format is [a-zA-Z0-9\-]+ in {name}'


class ERROR_INVALID_IMAGE_LENGTH(ERROR_INVALID_ARGUMENT):
    _message = 'The length of image should be less than equal {length} in {name}'


class ERROR_INVALID_TEMPLATE_SCHEMA(ERROR_INVALID_ARGUMENT):
    _message = 'Template schema format(JSON SCHEMA) is invalid. (key = {key})'


class ERROR_NO_IMAGE_IN_REGISTRY(ERROR_UNKNOWN):
    _message = 'Image does not found. (registry_type = {registry_type}, image = {image})'


class ERROR_REGISTRY_SETTINGS(ERROR_UNKNOWN):
    _message = 'Registry settings are not ready. (registry_type = {registry_type})'
