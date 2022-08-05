# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

# utility method
def get_question_fields(item):
    return {
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'author': item.creators and item.creators[0] or None,
        'closed': api.content.get_state(item) == 'closed',
        'text': item.text,
        'approved': item.approved,
        'deleted': api.content.get_state(item) == 'deleted',
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        'link': item.absolute_url(),
        'rel': item.absolute_url(1),
        'subs': item.answer_count(),
        'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
        'added_at': item.created() and item.created().asdatetime().isoformat() or '1976-04-29',
        'view_count': item.view_count(),
        'comment_count': item.commment_count(),
        'vote_up_count': item.voted_up_count(),
        'vote_down_count': item.voted_down_count(),
        'vote_count': item.points(),
        'tags': item.subjects or None,
        'followed_by': item.followed_by
    }

def get_answer_fields(item):
    comments = [get_comment_fields(c) for c in item.listFolderContents(contentFilter={"portal_type" : "qa Comment"})]
    return {
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'author': item.author,
        # 'closed': item.closed,
        'text': item.text,
        'approved': item.approved,
        'deleted': item.deleted,
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
        'comments': comments,
        'hasComments': len(comments) > 0,
    }

def get_comment_fields(item):
    return {
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'author': item.author,
        'text': item.text,
        'deleted': item.deleted,
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        'link': item.absolute_url(),
        'rel': item.absolute_url(1),
        'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
        'added_at': item.added_at and item.added_at.isoformat() or '1976-04-29',
        'view_count': int(len(item.viewed_by)),
    }

class RelatedObjectsGet(Service):

    @property
    def _related_objects(self):
        result = {
            'related-objects': {
                'answers': [],
                'comments': [],
                'parent': get_question_fields(self.context),
            }
        }
        for answer in self.context.listFolderContents(contentFilter={"portal_type" : "qa Answer"}):
            result['related-objects']['answers'].append(get_answer_fields(answer))
        
        for comment in self.context.listFolderContents(contentFilter={"portal_type" : "qa Comment"}):
            result['related-objects']['comments'].append(get_comment_fields(comment))

        return result 

    def reply(self):
        related_objects = self._related_objects
        return related_objects['related-objects']

class RelatedObjectsGetFollowers(Service):
    def reply(self):
        obj = self.context
        if self.context.portal_type != 'qa Question':
            return {
                'status': 'error',
                'message': 'wrong call',
                'data': {}
            }
        try:
            return {
                'status': 'ok',
                'message': 'all ok',
                'data': {
                    'count': len(obj.followed_by),
                    'followers': obj.followed_by
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'data': {}
            }

class RelatedObjectsGetSimilars(Service):
    def reply(self):
        try:
            all_q = [x.getObject() for x in api.content.find(context=self.context.getParentNode(), depth=1, portal_type='qa Question')]
            all_scores = [{'q':x,'s':len( set(x.subjects) & set(self.context.subjects) )} for x in all_q if x.id != self.context.id]
            similar = [get_question_fields(x['q']) for x in sorted(all_scores, key = lambda d: d['s'], reverse=True)[0:10]]
            return {
                'status': 'ok',
                'similar': similar
            }
        except:
            return {
                'status': 'error',
                'similar': []
            }

class RelatedObjectsGetFollowed(Service):
    def reply(self):
        try:
            # get all question, we should supposed we are on tree node
            all_q = [x.getObject() for x in api.content.find(context=self.context, depth=1, portal_type='qa Question')]
            # get current user's username
            username = api.user.get_current().getUserName()
            followed = [get_question_fields(i) for i in all_q if username in i.followed_by]
            return {
                'status': 'ok',
                'followed': followed
            }
        except Exception as e:
            return {
                'status': 'error',
                'followed': [],
                'msg': str(e)
            }

class RelatedObjectsGetQuestions(Service):

    @property
    def _related_objects(self):
        result = {
            'related-objects': {
                'items': [],
                'parent': None,
            }
        }
        for item in self.context.listFolderContents(contentFilter={"portal_type" : "qa Question"}):
            result['related-objects']['items'].append(get_question_fields(item))
        return result    

    def reply(self):
        related_objects = self._related_objects
        tmp = related_objects['related-objects']['items']
        # need to filter only questions
        only_question_objects = [ i for i in tmp if i['_meta']['type'] == 'Question' ]

        # before all need to sort
        print('before all')
        print('=========================')
        if self.request.has_key('sort_order') and self.request.has_key('sort_by'):
            sort_by = self.request.get('sort_by')
            sort_order = self.request.get('sort_order')
            print('sort by ' + sort_by)
            print('order ' + sort_order)
            #import pdb; pdb.set_trace()
            if sort_by == 'by_date':
                only_question_objects = sorted( only_question_objects,
                    key = lambda d: d['added_at'],
                    reverse = bool(sort_order == 'desc')
                )
            elif sort_by == 'by_activity':
                only_question_objects = sorted( only_question_objects,
                    key = lambda d: d['last_activity_at'],
                    reverse = bool(sort_order == 'desc')
                )
            elif sort_by == 'by_answers':
                only_question_objects = sorted( only_question_objects,
                    key = lambda d: d['subs'],
                    reverse = bool(sort_order == 'desc')
                )
            elif sort_by == 'by_votes':
                only_question_objects = sorted( only_question_objects,
                    key = lambda d: d['vote_count'],
                    reverse = bool(sort_order == 'desc')
                )
        else:
            # default sort 
            only_question_objects = sorted( only_question_objects,
                key = lambda d: d['added_at'],
                reverse = True
            )
        # there is text?
        if self.request.has_key('text'):
            text = self.request.get('text')
            _tmp_text = text.split(' ')
            _tmp_text = [i.lower() for i in _tmp_text]
            _tmp_text = set(_tmp_text)
            only_question_objects = [ i for i in only_question_objects if set([x.lower() for x in i['title'].split(' ')]).intersection(_tmp_text)]
            #only_question_objects = [ i for i in only_question_objects if text.lower() in i['title'].lower() ]

        # there is a tag setted?
        if self.request.has_key('tags'):
            tags = self.request.get('tags')
            only_question_objects = [ i for i in only_question_objects if tags in i['tags'] ]

        _start = 0
        _end = len(tmp)
        try:
            if self.request.has_key('start_at'):
                _start = int(self.request.get('start_at'))
            if self.request.has_key('end_at'):
                _end = int(self.request.get('end_at'))
        except:
            pass

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
