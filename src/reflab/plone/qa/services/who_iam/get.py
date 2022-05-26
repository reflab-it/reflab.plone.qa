# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

@implementer(IExpandableElement)
@adapter(Interface, Interface)
class WhoIam(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'who-iam': {
                '@id': '{}/@who-iam'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        # set default values:
        uid = None
        username = None
        user_full_name = None
        status = None
        
        # getting user data or none
        if api.user.is_anonymous():
            status = 'anonymous'
        else:
            status = 'logged'
            try:
                user_data = api.user.get_current()
                uid = user_data.id
                username = user_data.getUserName()
                user_full_name = user_data.getProperty('fullname')
            except:
                status = 'error'

        result = {
            'who-iam': {
                'status': status,
                'userid': uid,
                'username': username,
                'fullname': user_full_name
            }
        }

        # return data
        return result


class WhoIamGet(Service):

    def reply(self):
        tmp = WhoIam(self.context, self.request)
        return tmp(expand=True)['who-iam']