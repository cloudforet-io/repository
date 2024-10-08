from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel

__all__ = ["Plugin"]


class Plugin(MongoModel):
    """
    name is unique per domain
    """

    plugin_id = StringField(max_length=255, unique_with="domain_id")
    name = StringField(max_length=255)
    state = StringField(
        max_length=40, default="ENABLED", choices=("ENABLED", "DISABLED")
    )
    image = StringField(max_length=255)
    registry_type = StringField(max_length=255, default="DOCKER_HUB")
    registry_config = DictField()
    resource_type = StringField(max_length=255)
    provider = StringField(max_length=255, default=None, null=True)
    capability = DictField()
    labels = ListField(StringField(max_length=255))
    tags = DictField()
    docs = DictField(null=True, default=None)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    meta = {
        "updatable_fields": [
            "name",
            "state",
            "capability",
            "labels",
            "tags",
            "docs",
        ],
        "minimal_fields": [
            "plugin_id",
            "name",
            "state",
            "image",
            "registry_type",
            "resource_type",
            "provider",
        ],
        "ordering": ["name"],
        "indexes": [
            "plugin_id",
            "state",
            "registry_type",
            "resource_type",
            "provider",
            "domain_id",
        ],
    }
