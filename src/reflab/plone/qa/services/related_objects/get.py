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
                'last_activity_at': item.last_activity_at.isoformat(),
                'added_at': item.added_at.isoformat(),
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
        # need to filter only questions
        only_question_objects = [ i for i in tmp if i['_meta']['type'] == 'Question' ]
        only_question_objects = sorted( only_question_objects,
            key = lambda d: d['added_at'],
            reverse = True
        )
        _start = 0
        _end = len(tmp)
        try:
            if self.request.has_key('start_at'):
                _start = int(self.request.get('start_at'))
            if self.request.has_key('end_at'):
                _end = int(self.request.get('end_at'))
        except:
            pass
        
        # pagination ? or only let's user able to get item from x to y?
        
        if _end > _start:
            _tmp = only_question_objects[_start:_end]
        else:
            _tmp = only_question_objects

        return {
            'questions': _tmp,
            'total_questions': len(tmp)
        }
        return tmp