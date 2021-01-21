from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel

from spaceone.repository.model.repository_model import Repository

__all__ = ['Schema']


class SchemaTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class Schema(MongoModel):
    name = StringField(max_length=255, unique_with='domain_id')
    service_type = StringField(max_length=255)
    schema = DictField()
    labels = ListField(StringField(max_length=255))
    tags = ListField(EmbeddedDocumentField(SchemaTag))
    repository = ReferenceField('Repository', reverse_delete_rule=DENY)
    repository_id = StringField(max_length=40)
    project_id = StringField(max_length=255, default=None, null=True)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        'updatable_fields': [
            'name',
            'schema',
            'repository_id',
            'labels',
            'tags'
        ],
        'minimal_fields': [
            'name',
            'service_type'
        ],
        'change_query_keys': {
            'repository_id': 'repository.repository_id'
        },
        'reference_query_keys': {
            'repository': Repository
        },
        'ordering': ['name'],
        'indexes': [
            'name',
            'service_type',
            'repository',
            'project_id',
            'domain_id',
            ('tags.key', 'tags.value')
        ]
    }
