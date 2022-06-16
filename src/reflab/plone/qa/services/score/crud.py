# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import alsoProvides
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

def remove_and_add_if_need(item, first_data_set, second_data_set):
    action = ''
    if item in first_data_set:
        tmp = first_data_set
        tmp.remove(item)
        first_data_set = tmp
        action = "updated"
    else:
        if item not in second_data_set:
            tmp = second_data_set
            tmp.append(item)
            second_data_set = tmp
            action = "added"
        else:
            action = 'already'
    return action

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
        message = ''
        if userid is not None:
            message = remove_and_add_if_need(userid, self.context.vote_down_list, self.context.vote_up_list)
            return {
                'status': 'ok',
                'message': message,
                'count': int(len(self.context.vote_up_list)) - int(len(self.context.vote_down_list))
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
        message = ''
        if userid is not None:
            message = remove_and_add_if_need(userid, self.context.vote_up_list, self.context.vote_down_list)
            return {
                'status': 'ok',
                'message': message,
                'count': int(len(self.context.vote_up_list)) - int(len(self.context.vote_down_list))
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid suer'
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
                'vote_down': vote_down,
                'count': int(len(self.context.vote_up_list)) - int(len(self.context.vote_down_list))
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid user'
            }