from spaceone.core.error import *


class ERROR_NO_DASHBOARD_TEMPLATE(ERROR_INVALID_ARGUMENT):
    _message = 'Dashboard Template does not exists. (template_id = {template_id})'


class ERROR_MANAGED_REPOSITORY_NOT_SUPPORT_LIST(ERROR_INVALID_ARGUMENT):
    _message = 'Managed Repository does not support list method.'
