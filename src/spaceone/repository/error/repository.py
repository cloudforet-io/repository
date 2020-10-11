from spaceone.core.error import *


class ERROR_NO_REPOSITORY(ERROR_BASE):
    _message = 'Repository does not exists.'


class ERROR_REPOSITORY_BACKEND(ERROR_BASE):
    _status_code = 'INTERNAL'
    _message = 'Repository backend has problem. ({host})'

class ERROR_AWS_ECR_TOKEN(ERROR_BASE):
    _message = 'Failed to get ECR TOKEN, check IAM policy'
