# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from ...content.qa_folder import IQaFolder
from ...helpers import munge_search_term
from ...helpers import time_profiler
from ..fields import get_question_fields


@implementer(IExpandableElement)
@adapter(IQaFolder, Interface)
class Questions(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @time_profiler
    def __call__(self, expand=False):
        result = {
            "questions": {
                "@id": "{}/@get-questions".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result

        # CATALOG QUERY
        catalog = api.portal.get_tool('portal_catalog')

        query = dict(
            portal_type='qa Question',
            path='/'.join(self.context.getPhysicalPath()),
            sort_on='created',
            sort_order='descending'
        )

        sort_order = self.request.get('sort_order', None)
        sort_by = self.request.get('sort_by', None)
        text = self.request.get('text', None)
        tags = self.request.get('tags', None)
        filter_by = self.request.get('order_by', None)  # TODO, rename parameter

        if sort_order:
            query['sort_order'] = 'descending' if sort_order == 'desc' else 'ascending'

        sort_by_indexes_map = {
            'by_date': 'created',
            'by_activity': 'last_activity_at',
            'by_answer': 'answer_count',
            'by_votes': 'points',
        }
        if sort_by:
            query['sort_on'] = sort_by_indexes_map.get(sort_by)

        if text:
            query['SearchableText'] = munge_search_term(text)

        if tags:
            if type(tags) == str:
                tags = [tags]
            query['Subject'] = tags

        if filter_by and filter_by != 'ALL':
            if filter_by == 'UNANSWERED':
                query['answer_count'] = 0
            if filter_by == 'FOLLOWED':
                query['followed_by'] = api.user.get_current().getUserName()
            if filter_by == 'CLOSED':
                query['has_approved_answer'] = True

        items = catalog(**query)

        # BATCHING
        start_at = self.request.get('start_at', 0)
        end_at = self.request.get('end_at', 100)

        if start_at:
            start_at = int(start_at)
        else:
            start_at = 0

        if end_at:
            end_at = int(end_at)
        else:
            end_at = len(items)

        # QUESTION FIELDS
        results = []
        for item in items[start_at:end_at + 1]:
            results.append(get_question_fields(item, is_preview=True))

        result["questions"]['status'] = 'ok'
        result["questions"]['questions'] = results
        result["questions"]['total_questions'] = len(items)
        result["questions"]['page'] = int((end_at + 1) / 10)

        return result


class QuestionsGet(Service):
    def reply(self):
        questions = Questions(self.context, self.request)
        return questions(expand=True)["questions"]
