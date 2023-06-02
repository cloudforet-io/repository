from schematics.models import Model
from schematics.types import ListType, StringType, BooleanType


class Capability(Model):
    supported_schema = ListType(StringType())
    use_resource_secret = BooleanType(default=False)
    monitoring_type = StringType(choices=('METRIC', 'LOG'))
    supported_providers = ListType(StringType())
