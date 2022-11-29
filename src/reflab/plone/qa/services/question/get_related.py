# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from ...content.qa_question import IQaQuestion
from ..fields import get_question_fields


@implementer(IExpandableElement)
@adapter(IQaQuestion, Interface)
class Related(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "related": {
                "@id": "{}/@get-similars".format(self.context.absolute_url())
            }
        }

        if not expand:
            return result

        all_q = [x.getObject() for x in api.content.find(context=self.context.getParentNode(), depth=1, portal_type='qa Question')]
        all_scores = [{'q': x, 's': len(set(x.subjects) & set(self.context.subjects))} for x in all_q if x.id != self.context.id]
        similar = [get_question_fields(x['q']) for x in sorted(all_scores, key=lambda d: d['s'], reverse=True)[0:10]]
        result['related']['status'] = 'ok'
        result['related']['similar'] = similar
        return result


class RelatedGet(Service):
    def reply(self):
        questions = Related(self.context, self.request)
        return questions(expand=True)["related"]
