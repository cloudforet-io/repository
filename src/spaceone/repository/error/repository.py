from spaceone.core.error import *


class ERROR_INVALID_REPOSITORY_TYPE(ERROR_INVALID_ARGUMENT):
    _message = "Invalid repository type. (supported_types = local | remote | managed)"


class ERROR_NOT_UPDATE_MANAGED_REPOSITORY(ERROR_INVALID_ARGUMENT):
    _message = "Can not update managed repository."


class ERROR_LOCAL_REPOSITORY_ALREADY_EXIST(ERROR_INVALID_ARGUMENT):
    _message = "Local repository already exist."


class ERROR_ONLY_ONE_LOCAL_REPOSITORY_CAN_BE_REGISTERED(ERROR_INVALID_ARGUMENT):
    _message = "Only one local repository can be registered.(local_repository_count= {local_repository_count})"


class ERROR_ONLY_ONE_MANAGED_REPOSITORY_CAN_BE_REGISTERED(ERROR_INVALID_ARGUMENT):
    _message = "Only one managed repository can be registered.(managed_repository_count= {managed_repository_count})"


class ERROR_MANAGED_REPOSITORY_ALREADY_EXIST(ERROR_INVALID_ARGUMENT):
    _message = "Managed repository already exist."


class ERROR_REMOTE_REPOSITORY_ALREADY_EXIST(ERROR_INVALID_ARGUMENT):
    _message = "Remote repository already exist. (endpoint = {endpoint})"


class ERRROR_NOT_SET_UP_REMOTE_REPOSITORY(ERROR_INVALID_ARGUMENT):
    _message = "Remote repository is not set up."


class ERROR_SORT_KEY(ERROR_INVALID_ARGUMENT):
    _message = "Sort key is invalid. (sort_key = {sort_key})"


class ERROR_NOT_FOUND_REPOSITORY(ERROR_INVALID_ARGUMENT):
    _message = "Repository does not exist. (repository_id = {repository_id})"


class ERROR_REMOTE_REPOSITORY_AUTH_FAILURE(ERROR_INVALID_ARGUMENT):
    _message = "Remote repository authentication failure."
