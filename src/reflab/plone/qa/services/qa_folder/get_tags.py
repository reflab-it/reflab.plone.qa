# -*- coding: utf-8 -*-
from plone.api import content as content_api
from plone.api import user as user_api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

from ...content.qa_folder import IQaFolder
from ...helpers import get_user_settings

import logging

logger = logging.getLogger("Plone")

@implementer(IExpandableElement)
@adapter(IQaFolder, Interface)
class Tags(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'tags': {
                '@id': '{}/@tags-list'.format(
                    self.context.absolute_url(),
                ),
            },
        }

        if not expand:
            return result
        print(self.request.form)
        result = []
        logger.info('getting tags')

        followed_tags = []
        if 'followed' in self.request.keys():
            user = user_api.get_current()
            username = user.getUserName()
            user_settings = get_user_settings(username, self.context)
            if user_settings:
                followed_tags = user_settings.followed_tags

        questions = content_api.find(
            context=self.context, portal_type="qa Question"
        )

        for tag in self.context.datagrid_tags:
            approved_answers = []
            tag_questions = 0

            if 'stats' in self.request.keys():
                for question in questions:
                    if tag['uid'] in question.Subject:
                        tag_questions += 1
                        obj = question.getObject()
                        if obj.approved_answer and obj.approved_answer.to_object:
                            approved_answers.append(question)

            result.append({
                'id': tag['uid'],
                'name': tag['name'],
                'popular': tag['popular'],
                'description': tag['description'],
                'questions': tag_questions,
                'approved_answers': len(approved_answers),
                'followed': tag['uid'] in followed_tags
            })

        logger.info('returning tags')
        return result


class TagsGet(Service):

    def reply(self):
        tmp = Tags(self.context, self.request)
        return tmp(expand=True)
