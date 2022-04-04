# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class RelatedObjects(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        def get_field(item):
            return {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'author': item.author,
                'closed': item.closed,
                'text': item.text,
                'approved': item.approved,
                'deleted': item.deleted,
                'author': item.author,
                '_meta':
                {
                    'type': item.Type(),
                    'portal_type': item.portal_type
                },
                'link': item.absolute_url(),
                'rel': item.absolute_url(1),
                'subs': len(item.items()),
            }
        result = {
            'related-objects': {
                '@id': '{}/@related-objects'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result
        contents = [x.getObject() for x in api.content.find(context=self.context, depth=1)]
        #import pdb; pdb.set_trace()
        tmp = []
        parent = None
        if self.context.Type() == 'Question':
            parent = get_field(self.context)
        for i in contents:
            tmp.append(get_field(i))
        response = {
            'related-objects': {
                'items': tmp,
                'parent': parent,
            }
        }
        return response


class RelatedObjectsGet(Service):

    def reply(self):
        related_objects = RelatedObjects(self.context, self.request)
        return related_objects(expand=True)['related-objects']

class RelatedObjectsGetQuestions(Service):

    def reply(self):
        related_objects = RelatedObjects(self.context, self.request)
        tmp = related_objects(expand=True)['related-objects']['items']
        tmp = [ i for i in tmp if i['_meta']['type'] == 'Question' ]
        return tmp