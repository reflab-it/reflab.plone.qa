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
    first_modifid = False
    second_modifid = False
    if item in first_data_set:
        first_data_set.remove(item)
        action = "updated"
        first_modifid = True
    else:
        if item not in second_data_set:
            second_data_set.append(item)
            action = "added"
            second_modifid = True
        else:
            action = 'already'
    resp = {
        'action': action,
        'first_data_set': None,
        'second_data_set': None
    }
    if first_modifid: resp['first_data_set'] = first_data_set
    if second_modifid: resp['second_data_set'] = second_data_set
    return resp

class VoteUp(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        tmp = Vote(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        #import pdb; pdb.set_trace()
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            result = remove_and_add_if_need(userid, self.context.voted_down_by, self.context.voted_up_by)
            if result['first_data_set'] is not None:
                self.context.voted_down_by = result['first_data_set']
            if result['second_data_set'] is not None:
                self.context.voted_up_by = result['second_data_set']
            return {
                'status': 'ok',
                'message': result['action'],
                'count': int(len(self.context.voted_up_by)) - int(len(self.context.voted_down_by))
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
            result = remove_and_add_if_need(userid, self.context.voted_up_by, self.context.voted_down_by)
            if result['first_data_set'] is not None:
                self.context.voted_up_by = result['first_data_set']
            if result['second_data_set'] is not None:
                self.context.voted_down_by = result['second_data_set']
            return {
                'status': 'ok',
                'message': result['action'],
                'count': int(len(self.context.voted_up_by)) - int(len(self.context.voted_down_by))
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
            vote_up = userid in self.context.voted_down_by
            vote_down = userid in self.context.voted_down_by
            return {
                'status': 'ok',
                'vote_up': vote_up,
                'vote_down': vote_down,
                'count': int(len(self.context.voted_up_by)) - int(len(self.context.voted_down_by))
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid user'
            }