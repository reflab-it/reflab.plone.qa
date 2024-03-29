# -*- coding: utf-8 -*-
from plone.api import content as content_api
from plone.api import user as user_api
from plone.api import env as env_api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

from ...content.qa_folder import IQaFolder
from ..fields import get_question_fields


@implementer(IExpandableElement)
@adapter(IQaFolder, Interface)
class MyFollowed(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'my-followed': {
                '@id': '{}/@get-followed-questions'.format(
                    self.context.absolute_url(),
                ),
            },
        }

        if not expand:
            return result

        if 'userid' not in self.request.keys():
            username = user_api.get_current().getUserName()
        else:
            userid = self.request.get('userid')
            with env_api.adopt_roles(roles=['Manager']):
                userfolder = content_api.get(UID=userid)
            if not userfolder:
                raise KeyError('User folder for UID {userid} does not exists')
            username = userfolder.Title()

        questions = content_api.find(context=self.context, portal_type='qa Question', followed_by=username)
        followed = [get_question_fields(i) for i in questions]
        result['my-followed']['status'] = 'ok'
        result['my-followed']['followed'] = followed

        return result


class MyFollowedGet(Service):

    def reply(self):
        my_followed = MyFollowed(self.context, self.request)
        return my_followed(expand=True)["my-followed"]
