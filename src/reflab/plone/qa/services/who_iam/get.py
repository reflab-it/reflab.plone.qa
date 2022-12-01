# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection

from ..fields import get_question_fields
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

                # # Also create the user folder settings if it not exists
                for item in api.content.find(portal_type='qa Folder'):
                    qa_folder = item.getObject()
                    with api.env.adopt_roles(roles=['Manager']):
                        if get_user_settings(username, qa_folder) is None:
                            alsoProvides(self.request, IDisableCSRFProtection)
                            try:
                                create_user_settings(username, qa_folder)
                            except KeyError:
                                pass
            except Exception:
                raise Exception
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


class WhoIsGet(Service):

    def reply(self):
        user = None
        answ_list = []
        if 'user' in self.request.keys() and 'folder' in self.request.keys():
            user = self.request.get('user')
            plone_user_data = api.user.get(user)
            full_name = plone_user_data.getProperty('fullname')
            folder_mame = self.request.get('folder').replace('/', '')
            curfolder = [f for f in self.context.contentItems() if f[0] == folder_mame]
            try:
                _cur = curfolder[0][1]
                contents = [x.getObject() for x in api.content.find(context=_cur, depth=1, portal_type='qa Question', Creator=user)]
                answ_list = [x for x in contents if user in x.creators]
            except:
                answ_list = []
        else:
            return {
                'status': 'error',
                'message': 'missing user'
            }
        return {
            'status': 'ok',
            'message': 'draft',
            'username': user,
            'fullname': full_name,
            'answers': [get_question_fields(a) for a in answ_list]
        }