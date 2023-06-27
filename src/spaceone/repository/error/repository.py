from spaceone.core.error import *


class ERROR_INVALID_REPOSITORY_TYPE(ERROR_INVALID_ARGUMENT):
    _message = 'Invalid repository type. (supported_types = local | remote | managed)'


class ERROR_NOT_UPDATE_MANAGED_REPOSITORY(ERROR_INVALID_ARGUMENT):
    _message = 'Can not update managed repository.'


class ERROR_LOCAL_REPOSITORY_ALREADY_EXIST(ERROR_INVALID_ARGUMENT):
    _message = 'Local repository already exist.'


class ERROR_MANAGED_REPOSITORY_ALREADY_EXIST(ERROR_INVALID_ARGUMENT):
    _message = 'Managed repository already exist.'


class ERROR_REMOTE_REPOSITORY_ALREADY_EXIST(ERROR_INVALID_ARGUMENT):
    _message = 'Remote repository already exist. (endpoint = {endpoint})'


class ERRROR_NOT_SET_UP_REMOTE_REPOSITORY(ERROR_INVALID_ARGUMENT):
    _message = 'Remote repository is not set up.'
