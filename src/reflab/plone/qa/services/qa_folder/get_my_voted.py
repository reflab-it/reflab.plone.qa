# -*- coding: utf-8 -*-
from plone.api import content as content_api
from plone.api import user as user_api
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

        username = user_api.get_current().getUserName()

        voted_up_questions = content_api.find(
            context=self.context,
            portal_type='qa Question',
            voted_up_by=username
        )

        voted_down_questions = content_api.find(
            context=self.context,
            portal_type='qa Question',
            voted_down_by=username
        )

        voted_up_answers = content_api.find(
            context=self.context,
            portal_type='qa Answer',
            voted_up_by=username
        )

        voted_down_answers = content_api.find(
            context=self.context,
            portal_type='qa Answer',
            voted_down_by=username
        )

        questions = {}

        def _add_question(q):
            questions[q.UID()] = {
                'question': get_question_fields(q),
                'question_upvoted': False,
                'question_downvoted': False,
                'answer_upvotes': 0,
                'answer_downvotes': 0,
            }

        for item in voted_up_questions:
            uid = item.UID
            if uid not in questions.keys():
                _add_question(item.getObject())
            questions[uid]['question_upvoted'] = True

        for item in voted_down_questions:
            uid = item.UID
            if uid not in questions.keys():
                _add_question(item.getObject())
            questions[uid]['question_downvoted'] = True

        for item in voted_up_answers:
            question = item.getObject().aq_parent
            uid = question.UID()
            if uid not in questions.keys():
                _add_question(question)
            questions[uid]['answer_upvotes'] += 1

        for item in voted_down_answers:
            question = item.getObject().aq_parent
            uid = question.UID()
            if uid not in questions.keys():
                _add_question(question)
            questions[uid]['answer_downvotes'] += 1

        voted = [v for v in questions.values()]
        voted = sorted(voted, key=lambda d: d['question']['added_at'], reverse=True)

        result['my-voted']['status'] = 'ok'
        result['my-voted']['voted'] = voted
        return result


class MyVotedGet(Service):

    def reply(self):
        my_voted = MyVoted(self.context, self.request)
        return my_voted(expand=True)["my-voted"]
