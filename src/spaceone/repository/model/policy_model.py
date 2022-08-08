from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.repository.model.repository_model import Repository

__all__ = ['Policy']


class Policy(MongoModel):
    policy_id = StringField(max_length=255, required=True, unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    state = StringField(max_length=40, default='ENABLED', choices=('ENABLED', 'DISABLED'))
    permissions = ListField(StringField())
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
            'permissions',
            'repository_id',
            'labels',
            'tags'
        ],
        'minimal_fields': [
            'policy_id',
            'name'
        ],
        'change_query_keys': {
            'repository_id': 'repository.repository_id'
        },
        'reference_query_keys': {
            'repository': Repository
        },
        'ordering': ['name'],
        'indexes': [
            # 'policy_id',
            'name',
            'repository',
            'repository_id',
            'project_id',
            'domain_id',
        ]
    }
