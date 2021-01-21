from datetime import datetime
from mongoengine import *

from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel

from spaceone.repository.model.repository_model import Repository

__all__ = ['Plugin']


class PluginTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class Plugin(MongoModel):
    """
    name is unique per domain
    """
    plugin_id = StringField(max_length=40, generate_id='plugin', unique=True)
    name = StringField(max_length=255)
    state = StringField(max_length=40, default='ENABLED', choices=('ENABLED', 'DISABLED', 'DELETED'))
    image = StringField(max_length=255)
    registry_url = StringField(max_length=255)
    service_type = StringField(max_length=255)
    provider = StringField(max_length=255, default=None, null=True)
    capability = DictField()
    template = DictField()
    labels = ListField(StringField(max_length=255))
    tags = ListField(EmbeddedDocumentField(PluginTag))
    repository = ReferenceField('Repository', reverse_delete_rule=DENY)
    repository_id = StringField(max_length=40)
    project_id = StringField(max_length=255, default=None, null=True)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    deleted_at = DateTimeField(default=None, null=True)

    meta = {
        'updatable_fields': [
            'name',
            'state',
            'provider',
            'template',
            'capability',
            'repository_id',
            'labels',
            'tags',
            'deleted_at'
        ],
        'minimal_fields': [
            'plugin_id',
            'name',
            'state',
            'image',
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
            'plugin_id',
            'state',
            'service_type',
            'provider',
            'repository',
            'project_id',
            'domain_id',
            ('tags.key', 'tags.value')
        ]
    }

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.filter(state__ne='DELETED')

    @classmethod
    def create(cls, data):
        """ Unique per domain
        """
        plugin_vos = cls.filter(name=data['name'], domain_id=data['domain_id'])
        if plugin_vos.count() > 0:
            raise ERROR_NOT_UNIQUE(key='name', value=data['name'])

        return super().create(data)

    def update(self, data):
        """ Unique per domain
        """
        if 'name' in data:
            plugin_vos = self.filter(name=data['name'], domain_id=data['domain_id'], plugin_id__ne=self.plugin_id)
            if plugin_vos.count() > 0:
                raise ERROR_NOT_UNIQUE(key='name', value=data['name'])

        return super().update(data)

    def delete(self):
        self.update({
            'state': 'DELETED',
            'deleted_at': datetime.utcnow()
        })
