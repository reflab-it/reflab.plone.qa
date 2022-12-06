# -*- coding: utf-8 -*-
from plone.api import content as content_api
from plone.api import user as user_api
from plone.memoize import ram
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from time import time

from ...content.qa_folder import IQaFolder
from ...helpers import get_user_settings
from ...helpers import time_profiler

import logging

logger = logging.getLogger("Plone")


def _tags_stats_cachekey(method, self, qa_folder_uid):
    cache_time = str(time() // (60 * 30))  # 30 minutes
    return (qa_folder_uid, cache_time)


@implementer(IExpandableElement)
@adapter(IQaFolder, Interface)
class Tags(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @ram.cache(_tags_stats_cachekey)
    def stats(self, qa_folder_uid):
        result = {}
        qa_folder = content_api.get(UID=qa_folder_uid)
        if qa_folder is None:
            return result

        questions = content_api.find(
            context=qa_folder,
            portal_type="qa Question"
        )

        for question in questions:
            for tag in question.Subject:
                if tag not in result.keys():
                    result[tag] = {
                        'questions': 0,
                        'approved': 0
                    }
                result[tag]['questions'] += 1
                if question.has_approved_answer:
                    result[tag]['approved'] += 1

        return result


    @time_profiler
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

        followed_tags = []
        if 'followed' in self.request.keys():
            user = user_api.get_current()
            username = user.getUserName()
            user_settings = get_user_settings(username, self.context)
            if user_settings:
                followed_tags = user_settings.followed_tags

        stats = {}
        if 'stats' in self.request.keys():
            stats = self.stats(self.context.UID())

        for tag in self.context.datagrid_tags:
            result.append({
                'id': tag['uid'],
                'name': tag['name'],
                'popular': tag['popular'],
                'description': tag['description'],
                'questions': stats.get(tag['uid'], {}).get('questions', None),
                'approved_answers': stats.get(tag['uid'], {}).get('approved', None),
                'followed': tag['uid'] in followed_tags
            })

        return result


class TagsGet(Service):

    def reply(self):
        tmp = Tags(self.context, self.request)
        return tmp(expand=True)
