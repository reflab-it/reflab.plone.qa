# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from ...content.qa_question import IQaQuestion
from ..fields import get_question_fields
from ..fields import get_answer_fields
from ..fields import get_comment_fields


@implementer(IExpandableElement)
@adapter(IQaQuestion, Interface)
class Activity(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "activity": {
                "@id": "{}/@related-objects".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result

        result['activity']['parent'] = get_question_fields(self.context)
        result['activity']['comments'] = []
        result['activity']['answers'] = []

        for answer in self.context.listFolderContents(contentFilter={"portal_type": "qa Answer"}):
            result['activity']['answers'].append(get_answer_fields(answer))

        for comment in self.context.listFolderContents(contentFilter={"portal_type": "qa Comment"}):
            result['activity']['comments'].append(get_comment_fields(comment))

        return result


class ActivityGet(Service):
    def reply(self):
        questions = Activity(self.context, self.request)
        return questions(expand=True)["activity"]
