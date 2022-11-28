# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

from ...helpers import get_user_settings
from ...helpers import munge_search_term
from ...vocabularies import QuestionSubjectsVocabularyFactory


def get_user_fields(username):
    fallback = username.split('@')[0]
    result = {
        'fullname': fallback,
        'id': ''
    }
    us = get_user_settings(username)
    if us:
        display_name = getattr(us, 'display_name', None) or fallback
        result['fullname'] = display_name
        result['id'] = us.UID()
    else:
        plone_user = api.user.get(username=username)
        if plone_user:
            fullname = plone_user.getProperty('fullname', None) or fallback
            if fullname:
                result['fullname'] = fullname
    return result


# utility method
def get_question_fields(item):

    # A brute way to manage both brain and real objects...
    if hasattr(item, 'getObject'):
        obj = item.getObject()
    else:
        obj = item
        item = None

    author = obj.creators and obj.creators[0] or 'REMOVED USER'
    approved_answer = obj.approved_answer.to_object if obj.approved_answer else None

    subjects_vocabulary = QuestionSubjectsVocabularyFactory(obj)
    tags = []
    for tag in obj.subjects:
        if tag in subjects_vocabulary:
            term = subjects_vocabulary.getTerm(tag)
            tags.append({
                'id': term.value,
                'name': term.title
            })

    result = {
        'id': obj.id,
        'title': obj.title,
        'description': item and item.Description or '',  # The description is from the brain only
        'author': get_user_fields(author),
        'closed': api.content.get_state(obj) == 'closed',
        'text': obj.text and obj.text.output_relative_to(obj) or '',
        'approved': approved_answer and True or False,
        'approved_answer_user': {},
        'deleted': api.content.get_state(obj) == 'deleted',
        '_meta':
        {
            'type': obj.Type(),
            'portal_type': obj.portal_type
        },
        'link': obj.absolute_url(),
        'rel': obj.absolute_url(1),
        'subs': obj.answer_count(),
        # 'last_activity_at': obj.last_activity_at and obj.last_activity_at.isoformat() or '1976-04-29',
        'added_at': obj.created() and obj.created().asdatetime().isoformat() or '1976-04-29',
        'view_count': obj.view_count(),
        'comment_count': obj.commment_count(),
        'vote_up_count': obj.voted_up_count(),
        'vote_down_count': obj.voted_down_count(),
        'vote_count': obj.points(),
        'tags': tags,
        'followed_by': obj.followed_by
    }

    if result['approved']:
        approved_answer_username = approved_answer.creators and approved_answer.creators[0] or 'REMOVED USER'
        result['approved_answer_user'] = get_user_fields(approved_answer_username)

    return result


def get_answer_fields(item):
    comments = [get_comment_fields(c) for c in item.listFolderContents(contentFilter={"portal_type" : "qa Comment"})]
    author = item.creators and item.creators[0] or 'REMOVED USER'
    return {
        'id': item.id,
        # 'title': item.title,
        # 'description': item.description,
        'author': get_user_fields(author),
        'text': item.text and item.text.output_relative_to(item) or '',
        'approved': item.UID() == item.aq_parent.approved_answer,
        'deleted': api.content.get_state(item) == 'deleted',
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        'link': item.absolute_url(),
        'rel': item.absolute_url(1),
        # 'subs': len(item.items()),
        # 'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
        'added_at': item.created() and item.created().asdatetime().isoformat() or '1976-04-29',
        # 'view_count': int(len(item.viewed_by)),
        'vote_up_count': item.voted_up_count(),
        'vote_down_count': item.voted_down_count(),
        'vote_count': item.points(),
        'comments': comments,
        'hasComments': len(comments) > 0,
    }


def get_comment_fields(item):
    author = item.creators and item.creators[0] or 'REMOVED USER'
    return {
        'id': item.id,
        # 'title': item.title,
        # 'description': item.description,
        'author': get_user_fields(author),
        'text': item.text,
        'deleted': api.content.get_state(item) == 'deleted',
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        'link': item.absolute_url(),
        'rel': item.absolute_url(1),
        # 'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
        'added_at': item.created() and item.created().asdatetime().isoformat() or '1976-04-29',
        # 'view_count': int(len(item.viewed_by)),
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

        # getting username
        username = api.user.get_current().getUserName()
        if username not in self.context.viewed_by:
            tmp = self.context.viewed_by.copy()
            tmp.append(username)

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
    # get all question followed by crurrent user
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

class RelatedObjectsGetVoted(Service):
    # get all question voted by crurrent user
    def reply(self):
        try:
            # get all question, we should supposed we are on tree node
            all_q = [x.getObject() for x in api.content.find(context=self.context, depth=1, portal_type='qa Question')]
            # get current user's username
            username = api.user.get_current().getUserName()
            voted_up_list = [get_question_fields(i) for i in all_q if username in i.voted_up_by]
            voted_down_list = [get_question_fields(i) for i in all_q if username in i.voted_down_by]
            return {
                'status': 'ok',
                'voted': {
                    'up': voted_up_list,
                    'down': voted_down_list
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'voted': None,
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
        for item in self.context.getFolderContents(contentFilter={"portal_type": "qa Question"}):
            result['related-objects']['items'].append(get_question_fields(item))
        return result

    def reply(self):
        # CATALOG QUERY
        catalog = api.portal.get_tool('portal_catalog')

        query = dict(
            portal_type='qa Question',
            path='/'.join(self.context.getPhysicalPath()),
            sort_on='created',
            sort_order='descending'
        )

        sort_order = self.request.get('sort_order', None)
        sort_by = self.request.get('sort_by', None)
        text = self.request.get('text', None)
        tags = self.request.get('tags', None)
        filter_by = self.request.get('order_by', None)  # TODO, rename parameter

        if sort_order:
            query['sort_order'] = 'descending' if sort_order == 'desc' else 'ascending'

        sort_by_indexes_map = {
            'by_date': 'created',
            'by_activity': 'last_activity_at',
            'by_answers': 'answer_count',
            'by_votes': 'points',
        }
        if sort_by:
            query['sort_on'] = sort_by_indexes_map.get(sort_by)

        if text:
            query['SearchableText'] = munge_search_term(text)

        if tags:
            if type(tags) == str:
                tags = [tags]
            query['Subject'] = tags

        if filter_by and filter_by != 'ALL':
            if filter_by == 'UNANSWERED':
                query['answer_count'] = 0
            if filter_by == 'FOLLOWED':
                query['followed_by'] = api.user.get_current().getUserName()
            if filter_by == 'CLOSED':
                query['has_approved_answer'] = True

        items = catalog(**query)

        # BATCHING
        start_at = self.request.get('start_at', None)
        end_at = self.request.get('end_at', None)

        if start_at:
            start_at = int(start_at)
        else:
            start_at = 0

        if end_at:
            end_at = int(end_at)
        else:
            end_at = len(items)

        # QUESTION FIELDS
        results = []
        for item in items[start_at:end_at + 1]:
            results.append(get_question_fields(item))

        return {
            'status': 'ok',
            'questions': results,
            'total_questions': len(items),
            'number_of_current_result': len(results),
        }




class QuestionStats(Service):
    def reply(self):
        try:
            data = get_question_fields(self.context)
            result = {
                'status': 'ok',
                'data': {
                    'asked': data['added_at'],
                    'seen': data['view_count'],
                    'updated': data['last_activity_at'],
                }
            }
            return result

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'data': {}
            }

