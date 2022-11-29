# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service

from ..fields import get_question_fields


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
            all_scores = [{'q': x, 's': len(set(x.subjects) & set(self.context.subjects))} for x in all_q if x.id != self.context.id]
            similar = [get_question_fields(x['q']) for x in sorted(all_scores, key=lambda d: d['s'], reverse=True)[0:10]]
            return {
                'status': 'ok',
                'similar': similar
            }
        except Exception:
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
