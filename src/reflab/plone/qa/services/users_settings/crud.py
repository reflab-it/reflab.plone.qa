# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import alsoProvides
import plone.protect.interfaces

from reflab.plone.qa.content.qa_user_settings import frequency_on_followed_tags_values, frequency_on_followed_questions_values

@implementer(IExpandableElement)
@adapter(Interface, Interface)
class UserPrefs(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'userprefs': {
                '@id': '{}/@user-prefs'.format(
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
            'userprefs': {
                'status': status,
                'userid': uid,
            }
        }
        return result

class UserPrefsSet(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        tmp = UserPrefs(self.context, self.request)
        res = tmp(expand=True)['vote']
        userid = None
        if 'userid' in res:
            userid = res['userid']
        if userid is not None:
            # read params from request
            return {
                'status': 'ok',
                'message': '',
                'data': {}
            }
        else:
            return {
                'status': 'error',
                'message': 'invalid suer'
            }

class UserPrefsInfo(Service):

    def reply(self):
        tmp = UserPrefs(self.context, self.request)
        res = tmp(expand=True)['userprefs']
        userid = None
        if 'userid' in res:
            userid = res['userid']
            if userid is not None:
                api.env.adopt_roles(roles=['Manager'])
                if userid in self.context.objectIds():
                    followed_tags = getattr(self.context[userid], 'followed_tags', [])
                    frequency_on_followed_tags = getattr(self.context[userid], 'notification_frequency_on_followed_tags', 'Never')
                    frequency_on_followed_questions = getattr(self.context[userid], 'notification_frequency_on_followed_questions', 'Never')
                    return {
                        'status': 'ok',
                        'message': 'settings exist for %s' % userid,
                        'data': {
                            'followed_tags': followed_tags,
                            'frequency_on_followed_tags': frequency_on_followed_tags,
                            'frequency_on_followed_questions': frequency_on_followed_questions
                        }
                    }
                else:
                    return {
                        'status': 'ok',
                        'message': 'settings do notexist for %s' % userid,
                        'data': {
                            'followed_tags': [],
                            'frequency_on_followed_tags': 'Never',
                            'frequency_on_followed_questions': 'Never'
                        }
                    }
        return {
            'status': 'error',
            'message': 'invalid user'
        }

class UserPrefsSchema(Service):

    def reply(self):
        return {
            'status': 'ok',
            'data': {
                'frequency_on_followed_tags_values': frequency_on_followed_tags_values,
                'frequency_on_followed_questions_values': frequency_on_followed_questions_values
            }
        }
