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
        if api.user.is_anonymous():
            result = {
                'who-iam': {
                    'status': 'anonymous',
                    'userid': None
                }
            }
        else:
            uid = None
            user_data = api.user.get_current()
            if user_data is not None:
                uid = user_data.id
            result = {
                'who-iam': {
                    'status': 'logged',
                    'userid': uid
                }
            }
        return result


class WhoIamGet(Service):

    def reply(self):
        tmp = WhoIam(self.context, self.request)
        return tmp(expand=True)['who-iam']