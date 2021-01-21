from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.repository.model.repository_model import Repository

__all__ = ['Policy']


class PolicyTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class Policy(MongoModel):
    policy_id = StringField(max_length=40, generate_id='policy', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    permissions = ListField(StringField())
    labels = ListField(StringField(max_length=255))
    tags = ListField(EmbeddedDocumentField(PolicyTag))
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
            'policy_id',
            'name',
            'repository',
            'project_id',
            'domain_id',
            ('tags.key', 'tags.value')
        ]
    }
