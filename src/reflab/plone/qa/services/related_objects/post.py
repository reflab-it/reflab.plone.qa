# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class InsertPost(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = {
            'result': {
                'code': None,
                'data': None,
            }
        }
        return response


class InsertPostObj(Service):

    def reply(self):
        data = InsertPost(self.context, self.request)
        invalid_response = {
            'status': 'error',
            'message': 'invalid data'
        }

        _type = None
        _parent_type = None
        _parent_id = None

        _data_is_valid = True
        try:
            if self.request.has_key('type'):
                _type = self.request.get('type')
            if self.request.has_key('parent_type'):
                _parent_type = self.request.get('parent_type')
            if self.request.has_key('parent_id'):
                _parent_id = self.request.get('parent_id')
        except:
            _data_is_valid = False

        if _data_is_valid is not True:
            return invalid_response
        
        if _type is None or _parent_type is None or _parent_id is None:
            return invalid_response

        # create comment or response

        if _type == 'comment':
            pass

        if _type == 'response':
            pass 

        # import pdb; pdb.set_trace()

        return data()
