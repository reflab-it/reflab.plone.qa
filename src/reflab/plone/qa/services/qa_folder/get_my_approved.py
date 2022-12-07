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
class MyApproved(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'my-approved': {
                '@id': '{}/@get-approved-answers'.format(
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

        answers = content_api.find(context=self.context, portal_type='qa Answer', Creator=username)
        questions = [a.getObject().aq_parent for a in answers]
        followed = [get_question_fields(i) for i in questions]
        result['my-followed']['status'] = 'ok'
        result['my-followed']['followed'] = followed

        return result


class MyApprovedGet(Service):

    def reply(self):
        my_followed = MyApproved(self.context, self.request)
        return my_followed(expand=True)["my-approved"]
