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
            'tag-list': {
                '@id': '{}/@tag-list'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result

        # get all question
        contents = [x.getObject() for x in api.content.find(context=self.context, depth=1, portal_type='qa Question')]
        all_tags = []
        for question in contents:
            for tag in question.tags:
                all_tags.append(tag)

        result = {
            'tag-list': all_tags
        }

        # return data
        return result


class TagsGet(Service):

    def reply(self):
        tmp = Tags(self.context, self.request)
        raw_tags = tmp(expand=True)['tag-list']
        # unicizing
        return list(set(raw_tags))

class TagsInfo(Service):

    def reply(self):
        tmp = Tags(self.context, self.request)
        raw_tags = tmp(expand=True)['tag-list']
        tmp = {}
        for tag in raw_tags:
            if tag in tmp:
                tmp[tag] = tmp[tag] + 1
            else:
                tmp[tag] = 1
        return tmp

class BestTags(Service):

    def reply(self):
        tmp = Tags(self.context, self.request)
        raw_tags = tmp(expand=True)['tag-list']
        tmp = {}
        for tag in raw_tags:
            if tag in tmp:
                tmp[tag] = tmp[tag] + 1
            else:
                tmp[tag] = 1
        tmp = list(tmp.items())
        by_rank = sorted(tmp, key=lambda x: -x[1])
        top25 = [x[0] for x in by_rank[0:25]]
        return top25
