from mongoengine import *
from datetime import datetime

from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel

__all__ = ['Repository']


class Repository(MongoModel):
    repository_id = StringField(max_length=40, required=True)
    name = StringField(max_length=255)
    repository_type = StringField(max_length=255, choices=['local', 'remote', 'managed'])
    state = StringField(max_length=20, default='ENABLED')
    order = IntField(required=True)
    endpoint = StringField(max_length=255)
    version = StringField(max_length=16)
    secret_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    deleted_at = DateTimeField(default=None, null=True)

    meta = {
        'updatable_fields': [
            'name'
        ],
        'minimal_fields': [
            'repository_id',
            'name',
            'repository_type'
        ],
        'ordering': ['order', 'name'],
        'indexes': [
            'repository_id',
            'name',
            'repository_type'
        ]
    }