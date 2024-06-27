from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel

__all__ = ["DashboardTemplate"]


class DashboardTemplate(MongoModel):
    template_id = StringField(max_length=255, unique_with="domain_id")
    name = StringField(max_length=255)
    state = StringField(
        max_length=40, default="ENABLED", choices=("ENABLED", "DISABLED")
    )
    template_type = StringField(max_length=255, default="SINGLE")
    dashboards = ListField(DictField())
    labels = ListField(StringField(max_length=255))
    tags = DictField()
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "name",
            "state",
            "template_type",
            "dashboards",
            "labels",
            "tags",
        ],
        "minimal_fields": [
            "template_id",
            "name",
            "state",
            "template_type",
        ],
        "ordering": ["name"],
        "indexes": [
            "template_id",
            "state",
            "template_type",
            "domain_id",
        ],
    }
