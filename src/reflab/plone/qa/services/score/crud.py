# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

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
            except:
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
        tmp = Vote(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            # check if the user first voted against
            if userid in self.context.vote_down_list:
                self.context.vote_down_list.remove(userid)
            # check if he has not already voted
            message = ''
            if userid not in self.context.vote_up_list:
                self.context.vote_up_list.append(userid)
                message = 'added'
            else:
                message = 'already'
            return {
                'status': 'ok',
                'message': message
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid user'
            }

class VoteDown(Service):

    def reply(self):
        tmp = Vote(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            # check if the user voted in favor first
            if userid in self.context.vote_up_list:
                self.context.vote_up_list.remove(userid)
            # check if he has not already voted
            message = ''
            if userid not in self.context.vote_down_list:
                self.context.vote_down_list.append(userid)
                message = 'added'
            else:
                message = 'already'
            return {
                'status': 'ok',
                'message': message
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid user'
            }

class VoteInfo(Service):

    def reply(self):
        tmp = Vote(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            vote_up = userid in self.context.vote_down_list
            vote_down = userid in self.context.vote_down_list
            return {
                'status': 'ok',
                'vote_up': vote_up,
                'vote_down': vote_down
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid user'
            }