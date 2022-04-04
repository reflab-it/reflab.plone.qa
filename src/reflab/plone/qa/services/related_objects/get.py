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
        tmp = []
        #import pdb; pdb.set_trace()
        for i in contents:
            tmp.append({
                'id': i.id,
                'title': i.title,
                'description': i.description,
                'author': i.author,
                'closed': i.closed,
                'text': i.text,
                'approved': i.approved,
                'deleted': i.deleted,
                'author': i.author,
                '_meta':
                {
                    'type': i.Type(),
                    'portal_type': i.portal_type
                },
                'link': i.absolute_url(),
                'rel': i.absolute_url(1),
            })
        response = {
            'related-objects': tmp
        }
        return response


class RelatedObjectsGet(Service):

    def reply(self):
        related_objects = RelatedObjects(self.context, self.request)
        return related_objects(expand=True)['related-objects']

class RelatedObjectsGetQuestions(Service):

    def reply(self):
        related_objects = RelatedObjects(self.context, self.request)
        tmp = related_objects(expand=True)['related-objects']
        tmp = [ i for i in tmp if i['_meta']['type'] == 'Question' ]
        return tmp