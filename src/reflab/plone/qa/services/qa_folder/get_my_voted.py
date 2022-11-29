# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

from ...content.qa_folder import IQaFolder
from ..fields import get_question_fields


@implementer(IExpandableElement)
@adapter(IQaFolder, Interface)
class MyVoted(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'my-voted': {
                '@id': '{}/@get-voted-questions'.format(
                    self.context.absolute_url(),
                ),
            },
        }

        if not expand:
            return result

        all_q = [x.getObject() for x in api.content.find(context=self.context, depth=1, portal_type='qa Question')]
        username = api.user.get_current().getUserName()
        voted_up_list = [get_question_fields(i) for i in all_q if username in i.voted_up_by]
        voted_down_list = [get_question_fields(i) for i in all_q if username in i.voted_down_by]
        result['my-voted']['status'] = 'ok'
        result['my-voted']['voted'] = {
            'up': voted_up_list,
            'down': voted_down_list
        }
        return result


class MyVotedGet(Service):

    def reply(self):
        my_voted = MyVoted(self.context, self.request)
        return my_voted(expand=True)["my-voted"]
