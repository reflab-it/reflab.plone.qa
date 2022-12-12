# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

from ..fields import get_question_fields


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class WhoIs(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'who-is': {
                '@id': '{}/@who-is'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        result['who-is'] = {
            'status': 'error',
            'message': 'Error on getting user info',
            'fullname': '',
            'answers': [],
        }

        userid = self.request.get('user', None)
        if not userid:
            result['who-is']['message'] = 'Missing user parameter'
            return result

        with api.env.adopt_roles(roles=['Manager']):
            userfolder = api.content.get(UID=userid)
        if not userfolder:
            result['who-is']['message'] = 'Missing user folder'

        result['who-is']['fullname'] = userfolder.display_name

        questions = api.content.find(
            context=self.context,
            portal_type='qa Question',
            Creator=userfolder.Title()
        )
        #result['who-is']['answers'] = [get_question_fields(q) for q in questions]
        result['who-is']['status'] = 'ok'
        result['who-is']['message'] = ''
        return result


class WhoIsGet(Service):

    def reply(self):
        tmp = WhoIs(self.context, self.request)
        return tmp(expand=True)['who-is']
