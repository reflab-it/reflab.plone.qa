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
class MyAnswered(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'my-answered': {
                '@id': '{}/@get-answered-questions"'.format(
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

        answers = content_api.find(
            context=self.context,
            portal_type='qa Answer',
            Creator=username,
            is_approved_answer=False
        )

        questions = []
        for answer in answers:
            question = answer.getObject().aq_parent
            questions.append(get_question_fields(question))

        result['my-answered']['status'] = 'ok'
        result['my-answered']['answered'] = questions

        return result


class MyAnsweredGet(Service):

    def reply(self):
        my_followed = MyAnswered(self.context, self.request)
        return my_followed(expand=True)["my-answered"]
