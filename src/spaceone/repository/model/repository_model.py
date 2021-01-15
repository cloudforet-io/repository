from mongoengine import *
from datetime import datetime

from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel

__all__ = ['Repository']


class Repository(MongoModel):
    repository_id = StringField(max_length=40, generate_id='repo', unique=True)
    name = StringField(max_length=255)
    repository_type = StringField(max_length=255)
    state = StringField(max_length=20, default='ENABLED')
    endpoint = StringField(max_length=255)
    version = StringField(max_length=16)
    secret_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    deleted_at = DateTimeField(default=None, null=True)

    meta = {
        'updatable_fields': [
            'name',
            'secret_id',
            'state',
            'deleted_at'
        ],
        'minimal_fields': [
            'repository_id',
            'name',
            'repository_type'
        ],
        'ordering': ['name'],
        'indexes': [
            'repository_id',
            'name',
            'repository_type'
        ]
    }

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.filter(state__ne='DELETED')

    @classmethod
    def create(cls, data):
        rr_vos = cls.filter(name=data['name'])
        if rr_vos.count() > 0:
            raise ERROR_NOT_UNIQUE(key='name', value=data['name'])

        return super().create(data)

    def update(self, data):
        if 'name' in data:
            rr_vos = self.filter(name=data['name'], repository_id__ne=self.repository_id)
            if rr_vos.count() > 0:
                raise ERROR_NOT_UNIQUE(key='name', value=data['name'])

        return super().update(data)

    def delete(self):
        self.update({
            'state': 'DELETED',
            'deleted_at': datetime.utcnow()
        })
