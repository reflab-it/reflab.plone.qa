# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Tags(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'tags-list': {
                '@id': '{}/@tags-list'.format(
                    self.context.absolute_url(),
                ),
            },
        }

        if not expand:
            return result

        result = []
        for i in self.context.datagrid_tags:
            questions = api.content.find(portal_type="qa Question", Subject=i['name'])
            approved_answers = []
            for question in questions:
                obj = question.getObject()
                if obj.approved_answer and obj.approved_answer.to_object:
                    approved_answers.append(question)
            result.append({
                'id': i['uid'],
                'name': i['name'],
                'popular': i['popular'],
                'description': i['description'],
                'questions': len(questions),
                'approved_answers': len(approved_answers)
            })

        return result


class TagsGet(Service):

    def reply(self):
        tmp = Tags(self.context, self.request)
        return tmp(expand=True)
