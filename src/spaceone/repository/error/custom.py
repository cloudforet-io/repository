from spaceone.core import error


class ERROR_REPOSITORY_BACKEND(error.ERROR_BASE):
    _status_code = 'INTERNAL'
    _message = 'Repository backend has problem. ({host})'


class ERROR_LOCAL_REPOSITORY_NOT_EXIST(error.ERROR_BASE):
    _message = 'Local Repository does not exist. (repository_type = local)'
