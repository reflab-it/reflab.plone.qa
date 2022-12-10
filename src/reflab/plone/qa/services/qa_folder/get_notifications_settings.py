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
class NotificationsSettings(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'notifications-settings': {
                '@id': '{}/@notifications-settings'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        result['notifications-settings']['status'] = 'error'
        result['notifications-settings']['message'] = 'An error occurred'
        result['notifications-settings']['data'] = {
            'frequency_on_followed_tags': 'Never',
            'frequency_on_followed_questions': 'Never'
        }

        if not api.user.is_anonymous():
            plone_user = api.user.get_current()
            username = plone_user.getUserName()

            # Also create the user folder settings if it not exists
            qa_folder = self.context
            with api.env.adopt_roles(roles=['Manager']):
                user_settings = get_user_settings(username, qa_folder)
                if user_settings is None:
                    alsoProvides(self.request, IDisableCSRFProtection)
                    user_settings = create_user_settings(username, qa_folder)
                frequency_on_followed_tags = getattr(user_settings, 'notification_frequency_on_followed_tags', 'Never')
                result['notifications-settings']['data']['frequency_on_followed_tags'] = frequency_on_followed_tags
                frequency_on_followed_questions = getattr(user_settings, 'notification_frequency_on_followed_questions', 'Never')
                result['notifications-settings']['data']['frequency_on_followed_questions'] = frequency_on_followed_questions
                result['notifications-settings']['status'] = 'ok'
                result['notifications-settings']['message'] = ''

        return result


class NotificationsSettingsGet(Service):

    def reply(self):
        tmp = NotificationsSettings(self.context, self.request)
        return tmp(expand=True)['notifications-settings']
