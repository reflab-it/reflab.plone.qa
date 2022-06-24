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
        print('init ')
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        print('call ')
        print("expand? " +str(expand))
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
                'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
                'added_at': item.added_at and item.added_at.isoformat() or '1976-04-29',
                'view_count': int(len(item.viewed_by)),
                'vote_up_count': int(len(item.vote_up_list)),
                'vote_down_count': int(len(item.vote_down_list)),
                'vote_count': int(len(item.vote_up_list)) - int(len(item.vote_down_list)),
                'tags': item.tags or None
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
        if self.context.portal_type == 'qa Folder':
            contents = [x.getObject() for x in api.content.find(context=self.context, depth=1, portal_type='qa Question')]
        else:
            contents = [x.getObject() for x in api.content.find(context=self.context, depth=1)]
        tmp = []
        parent = None
        full_tree = False
        print("full_tree?? " + str(full_tree))
        if self.context.Type() == 'Question':
            parent = get_field(self.context)
            full_tree = True
        for i in contents:
            anws = get_field(i)
            anws['comments'] = []
            anws['hasComments'] = False
            if full_tree:
                comments = [x.getObject() for x in api.content.find(context=i, depth=1)]
                if len(comments) > 0:
                    anws['hasComments'] = True  
                    for com in comments:
                        anws['comments'].append(get_field(com))
            tmp.append(anws)
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
        # there is text?
        if self.request.has_key('text'):
            text = self.request.get('text')
            only_question_objects = [ i for i in only_question_objects if text in i['title'] ]
        _start = 0
        _end = len(tmp)
        try:
            if self.request.has_key('start_at'):
                _start = int(self.request.get('start_at'))
            if self.request.has_key('end_at'):
                _end = int(self.request.get('end_at'))
        except:
            pass

        print('before return')
        print('=========================')
        if self.request.has_key('order_by'):
            custom_order = self.request.get('order_by')
            if custom_order in ['#', 'ALL', 'UNANSWERED', 'FOLLOWED', 'CLOSED']:
                # xxx ordering
                print('ordering by: ' + custom_order)
                if custom_order in ['#', 'ALL']:
                    pass
                else:
                    if custom_order == 'UNANSWERED':
                        print('order by => UNANSWERED')
                        _filtered = [q for q in only_question_objects if q['subs'] == 0]
                        #import pdb; pdb.set_trace()
                        only_question_objects = _filtered
                    elif custom_order == 'FOLLOWED':
                        print('order by => FOLLOWED')
                        pass
                    elif custom_order == 'CLOSED':
                        _filtered = [q for q in only_question_objects if q['closed'] == True]
                        only_question_objects = _filtered
            else:
                return {
                    'status': 'error',
                    'message': 'wrong ordering'
                }
        if _end > _start:
            try:
                _tmp = only_question_objects[_start:_end+1]
            except:
                print('however, something went quite wrong')
                _tmp = only_question_objects    
        else:
            _tmp = only_question_objects
        return {
            'status': 'ok',
            'questions': _tmp,
            'total_questions': len(only_question_objects),
            'number_of_current_result': len(_tmp),
        }
