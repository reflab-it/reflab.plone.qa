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

        all_q = [x.getObject() for x in api.content.find(context=self.context, depth=1, portal_type='qa Question')]
        username = api.user.get_current().getUserName()
        followed = [get_question_fields(i) for i in all_q if username in i.followed_by]
        result['my-followed']['status'] = 'ok'
        result['my-followed']['followed'] = followed

        return result


class MyFollowedGet(Service):

    def reply(self):
        my_followed = MyFollowed(self.context, self.request)
        return my_followed(expand=True)["my-followed"]
