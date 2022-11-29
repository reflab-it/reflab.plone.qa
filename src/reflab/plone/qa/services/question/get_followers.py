# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from ...content.qa_question import IQaQuestion


@implementer(IExpandableElement)
@adapter(IQaQuestion, Interface)
class Followers(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "followers": {
                "@id": "{}/@get-followers".format(self.context.absolute_url())
            }
        }

        if not expand:
            return result

        obj = self.context
        result['followers']['status'] = 'ok'
        result['followers']['message'] = 'all ok'
        result['followers']['data'] = {
            'count': len(obj.followed_by),
            'followers': obj.followed_by
        }

        return result


class FollowersGet(Service):
    def reply(self):
        questions = Followers(self.context, self.request)
        return questions(expand=True)["followers"]
