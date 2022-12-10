# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

from ...content.qa_user_settings import frequency_on_followed_tags_values
from ...content.qa_user_settings import frequency_on_followed_questions_values


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class NotificationsOptions(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'notifications-options': {
                '@id': '{}/@notifications-options'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        result['notifications-options']['status'] = 'ok'
        result['notifications-options']['data'] = {
            'frequency_on_followed_tags_values': frequency_on_followed_tags_values,
            'frequency_on_followed_questions_values': frequency_on_followed_questions_values
        }

        return result


class NotificationsOptionsGet(Service):

    def reply(self):
        tmp = NotificationsOptions(self.context, self.request)
        return tmp(expand=True)['notifications-options']
