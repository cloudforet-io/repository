from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel

from spaceone.repository.model.repository_model import Repository

__all__ = ['Schema']


class Schema(MongoModel):
    name = StringField(max_length=255, unique_with='domain_id')
    service_type = StringField(max_length=255)
    schema = DictField()
    labels = ListField(StringField(max_length=255))
    tags = DictField()
    repository = ReferenceField('Repository', reverse_delete_rule=DENY)
    project_id = StringField(max_length=255, default=None, null=True)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'schema',
            'labels',
            'tags'
        ],
        'exact_fields': [
            'name',
            'project_id',
            'domain_id',
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
            'domain_id'
        ],
        'aggregate': {
            'lookup': {
                'repository': {
                    'from': 'repository'
                }
            }
        }
    }
