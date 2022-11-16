# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

@implementer(IExpandableElement)
@adapter(Interface, Interface)
class UserSets(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'settings-list': {
                '@id': '{}/@settings-list'.format(
                    self.context.absolute_url(),
                ),
            },
        }
        if not expand:
            return result
        result = {
            'settings-list':[],
        }

        # return data
        return result


class UserSetsGet(Service):

    def reply(self):
        tmp = UserSets(self.context, self.request)
        return tmp(expand=True)['result']
        
class UserSetGet(Service):

    def reply(self):
        return [];
