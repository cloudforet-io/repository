from schematics.models import Model
from schematics.types import ListType, StringType, BooleanType


class Capability(Model):
    supported_schema = ListType(StringType())
