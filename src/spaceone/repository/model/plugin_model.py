from datetime import datetime
from mongoengine import *

from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel

from spaceone.repository.model.repository_model import Repository

__all__ = ['Plugin']


class Plugin(MongoModel):
    """
    name is unique per domain
    """
    plugin_id = StringField(max_length=255, unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    state = StringField(max_length=40, default='ENABLED', choices=('ENABLED', 'DISABLED'))
    image = StringField(max_length=255)
    registry_type = StringField(max_length=255, default='DOCKER_HUB')
    registry_config = DictField()
    service_type = StringField(max_length=255)
    provider = StringField(max_length=255, default=None, null=True)
    capability = DictField()
    template = DictField()
    labels = ListField(StringField(max_length=255))
    tags = DictField()
    repository = ReferenceField('Repository', reverse_delete_rule=DENY)
    repository_id = StringField(max_length=40)
    project_id = StringField(max_length=255, default=None, null=True)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        'updatable_fields': [
            'name',
            'state',
            'provider',
            'template',
            'capability',
            'repository_id',
            'labels',
            'tags'
        ],
        'minimal_fields': [
            'plugin_id',
            'name',
            'state',
            'image',
            'registry_type',
            'service_type',
            'provider'
        ],
        'change_query_keys': {
            'repository_id': 'repository.repository_id'
        },
        'reference_query_keys': {
            'repository': Repository
        },
        'ordering': ['name'],
        'indexes': [
            # 'plugin_id',
            'state',
            'registry_type',
            'service_type',
            'provider',
            'repository',
            'repository_id',
            'project_id',
            'domain_id',
        ]
    }
