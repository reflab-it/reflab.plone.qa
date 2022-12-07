# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection

from ...helpers import get_user_settings
from ...helpers import create_user_settings

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

        status = 'anonymous'
        userid = None
        fullname = None
        username = None

        # getting user data or none
        if not api.user.is_anonymous():
            status = 'logged'

            plone_user = api.user.get_current()
            username = plone_user.getUserName()
            fullname = plone_user.getProperty('fullname')

            # Also create the user folder settings if it not exists
            qa_folder = self.context
            with api.env.adopt_roles(roles=['Manager']):
                user_settings = get_user_settings(username, qa_folder)
                if user_settings is None:
                    alsoProvides(self.request, IDisableCSRFProtection)
                    user_settings = create_user_settings(username, qa_folder)
                userid = user_settings.UID()

        result = {
            'who-iam': {
                'status': status,
                'userid': userid,
                'username': username,
                'fullname': fullname
            }
        }

        return result


class WhoIamGet(Service):

    def reply(self):
        tmp = WhoIam(self.context, self.request)
        return tmp(expand=True)['who-iam']
