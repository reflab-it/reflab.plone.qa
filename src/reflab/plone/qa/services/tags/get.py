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
        # old compatible api
        all_tags = [i['name'] for i in self.context.datagrid_tags]
        # all information
        raw = [{'id': i['uid'], 
                'name': i['name'],
                'popular': i['popular'],
                'description': i['description'] } for i in self.context.datagrid_tags]
        popular = [i['name'] for i in raw if i['popular']]
        result = {
            'tag-list': all_tags,
            'raw': raw,
            'popular': popular,
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
        by_rank = []
        all_tags = None
        fast_way = True #False
        if not fast_way:
            contents = [x.getObject() for x in api.content.find(context=self.context, depth=1, portal_type='qa Question')]
            all_tags = []
            for question in contents:
                if question.subjects is not None:
                    for tag in question.subjects:
                        all_tags.append(tag)
            tmp = {}
            for tag in all_tags:
                if tag in tmp:
                    tmp[tag] = tmp[tag] + 1
                else:
                    tmp[tag] = 1
            tmp = list(tmp.items())
            by_rank = sorted(tmp, key=lambda x: -x[1])
            top25 = [x[0] for x in by_rank[0:25]]
        else:
            # fast reading from inserted tags
            tmp = Tags(self.context, self.request)
            all_tags = tmp(expand=True)['popular']
            top25 = [x for x in all_tags[0:25]]
        
        return top25
