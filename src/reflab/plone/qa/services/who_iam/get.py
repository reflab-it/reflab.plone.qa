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

class WhoIsGet(Service):

    def get_field(self, item):
        return {
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'author': item.author,
            'closed': item.closed,
            'text': item.text,
            'approved': item.approved,
            'deleted': item.deleted,
            '_meta':
            {
                'type': item.Type(),
                'portal_type': item.portal_type
            },
            'link': item.absolute_url(),
            'rel': item.absolute_url(1),
            'subs': len(item.items()),
            'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
            'added_at': item.added_at and item.added_at.isoformat() or '1976-04-29',
            'view_count': int(len(item.viewed_by)),
            'vote_up_count': int(len(item.vote_up_list)),
            'vote_down_count': int(len(item.vote_down_list)),
            'vote_count': int(len(item.vote_up_list)) - int(len(item.vote_down_list)),
            'tags': item.tags or None
        }

    def reply(self):
        user = None
        answ_list = []
        if self.request.has_key('user') and self.request.has_key('folder'):
            # xxx chiamata ad accounts?
            user = self.request.get('user')
            folder_mame = self.request.get('folder').replace('/', '')
            curfolder = [f for f in self.context.contentItems() if f[0] == folder_mame]
            try:
                _cur = curfolder[0][1]
                contents = [x.getObject() for x in api.content.find(context=_cur, depth=1, portal_type='qa Question', author=user)]
                answ_list = [x for x in contents if x.author == user]
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
            'fullname': user,
            'answers': [self.get_field(a) for a in answ_list]
        }