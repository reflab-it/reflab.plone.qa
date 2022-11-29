# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from ...content.qa_question import IQaQuestion
from ..fields import get_question_fields


@implementer(IExpandableElement)
@adapter(IQaQuestion, Interface)
class Stats(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "stats": {
                "@id": "{}/@get-question-stat".format(self.context.absolute_url())
            }
        }

        if not expand:
            return result

        data = get_question_fields(self.context)
        result['stats']['status'] = 'ok'
        result['stats']['data'] = {
            'asked': data['added_at'],
            'seen': data['view_count'],
            'updated': '',
        }
        return result


class StatsGet(Service):
    def reply(self):
        questions = Stats(self.context, self.request)
        return questions(expand=True)["stats"]
