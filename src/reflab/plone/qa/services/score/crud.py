# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import alsoProvides
from ..fields import get_user_fields
from ...content.qa_answer import IQaAnswer
from ...content.qa_question import IQaQuestion
from ...helpers import can_user_vote
import plone.protect.interfaces

@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Vote(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'vote': {
                '@id': '{}/@vote-info'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        if api.user.is_anonymous():
            status = 'anonymous'
        else:
            status = 'logged'
            try:
                user_data = api.user.get_current()
                uid = user_data.id
            except Exception:
                status = 'error'

        result = {
            'vote': {
                'status': status,
                'userid': uid,
            }
        }

        # return data
        return result

class VoteUp(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        tmp = Vote(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            if userid in self.context.voted_down_by:
                # user has voted down, can't vote up
                return {
                    'status': 'error',
                    'message': 'unable to vote up',
                    'action': 'none'
                }
            tmp_arr = self.context.voted_up_by
            action = ''
            if userid in self.context.voted_up_by:
                # user remove its vote
                tmp_arr.remove(userid)
                action = 'removed'
            else:
                # user add its vote
                tmp_arr.append(userid)
                action = 'upvoted'
            # update
            if not can_user_vote(self.context):
                raise Unauthorized("User can't vote")
            self.context.voted_up_by = tmp_arr
            self.context.reindexObject(idxs=['voted_up_by'])
            return {
                'status': 'ok',
                'action': action,
                'message': ''
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid suer'
            }

class VoteDown(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        tmp = Vote(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            if userid in self.context.voted_up_by:
                # user has voted down, can't vote up
                return {
                    'status': 'error',
                    'message': 'unable to vote down',
                    'action': 'none'
                }
            tmp_arr = self.context.voted_down_by
            action = ''
            if userid in self.context.voted_down_by:
                # user remove its vote
                tmp_arr.remove(userid)
                action = 'removed'
            else:
                # user add its vote
                tmp_arr.append(userid)
                action = 'downvoted'
            # update
            if not can_user_vote(self.context):
                raise Unauthorized("User can't vote")
            self.context.voted_down_by = tmp_arr
            self.context.reindexObject(idxs=['voted_down_by'])
            return {
                'status': 'ok',
                'action': action,
                'message': ''
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid suer'
            }

class VoteInfo(Service):

    def reply(self):
        if IQaQuestion.providedBy(self.context):
            qa_folder = self.context.aq_parent
        elif IQaAnswer.providedBy(self.context):
            qa_folder = self.context.aq_parent.aq_parent
        else:
            raise KeyError('invalid parent')

        tmp = Vote(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            voted_up_by = self.context.voted_up_by
            voted_down_by = self.context.voted_down_by
            voted_up = userid in voted_up_by
            voted_down = userid in voted_down_by
            voted_up_by_list = []
            voted_down_by_list = []
            for username in voted_up_by:
                voted_up_by_list.append(get_user_fields(username, qa_folder))
            for username in voted_down_by:
                voted_down_by_list.append(get_user_fields(username, qa_folder))

            return {
                'status': 'ok',
                'voted_up': voted_up,
                'voted_down': voted_down,
                'votes_up': len(voted_up_by),
                'votes_down': len(voted_down_by),
                'voted_up_by': voted_up_by_list,
                'voted_down_by': voted_down_by_list,
                'score': int(len(self.context.voted_up_by)) - int(len(self.context.voted_down_by))
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid user'
            }