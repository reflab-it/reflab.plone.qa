# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import alsoProvides
from plone.app.textfield.value import RichTextValue
from datetime import datetime
import plone.protect.interfaces
import json
import uuid


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
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = InsertPost(self.context, self.request)
        invalid_response = {
            'status': 'error',
            'message': 'invalid data'
        }
        _type = None
        _parent_type = None
        _parent_id = None
        _data_is_valid = True
        user_name = None

        post_data = self.request['BODY'] or None

        if api.user.is_anonymous() or post_data == None:
            return invalid_response

        data = {}
        response = {}
        try:
            user_name = api.user.get_current().getUserName()
            data = json.loads(post_data)
            _type = data.get('type')
            _parent_type = data.get('parent_type')
            _parent_id = data.get('parent_id')
        except:
            _data_is_valid = False

        if _data_is_valid is not True:
            return invalid_response

        if _type is None or _parent_type is None or _parent_id is None:
            return invalid_response

        # check type
        if _type not in ['question', 'comment', 'reply']:
            return {
                'status': 'error',
                'message': 'invalid type'
            }

        # create comment or response
        if _type == 'question':
            obj = api.content.find(context=self.context, id=_parent_id)
            folder = obj[0].getObject()
            try:
                _title = data.get('title')
                if _title is None or _title == '' or len(_title) < 3:
                    response['status'] = 'error'
                    response['message'] = 'unable to created, missing title'
                else:
                    res = api.content.create(
                        container=folder,
                        type='qa Question',
                        subjects=data.get('tags'),
                        title=_title,
                        creators=(user_name,),
                        added_at=datetime.now(),
                        text = RichTextValue(
                            raw=data.get('data') or '',
                            outputMimeType='text/plain'
                        )
                    )
                    response['status'] = 'ok'
                    response['message'] = 'created'
            except:
                response['status'] = 'error'
                response['message'] = 'unable to created'

        elif _type == 'comment':
            try:
                obj = api.content.find(context=self.context, id=_parent_id)
                parent = obj[0].getObject()
                res = api.content.create(
                    container=parent,
                    type='qa Comment',
                    id=str(uuid.uuid4()),
                    creators=(user_name,),
                    added_at=datetime.now(),
                    text=data.get('data') or ''
                )
                response['status'] = 'ok'
                response['message'] = 'created'
            except:
                response['status'] = 'error'
                response['message'] = 'unable to created'

        elif _type == 'reply':
            # getting base object
            obj = api.content.find(context=self.context, id=_parent_id)
            question = obj[0].getObject()
            try:
                res = api.content.create(
                    container=question,
                    type='qa Answer',
                    id=str(uuid.uuid4()),
                    creators=(user_name,),
                    added_at=datetime.now(),
                    text = RichTextValue(
                        raw=data.get('data') or '',
                        outputMimeType='text/plain'
                    )
                )
                response['status'] = 'ok'
                response['message'] = 'created'
            except:
                response['status'] = 'error'
                response['message'] = 'unable to created'
        
        else:
            response['status'] = 'error'
            response['message'] = 'unable to created, wrong type'


        response['id'] = res.id or None
        return response

class QuestionFollow(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        
        response = {
            'status': '',
            'msg': '',
            'data': {}
        }

        try:
            # getting user by session
            username = api.user.get_current().getUserName()
            # but getting action from posted data
            post_data = self.request['BODY'] or None
            data = json.loads(post_data)
            tmp = None # reference array
            if data['action'] == 'add':
                if username not in self.context.followed_by:
                    tmp = self.context.followed_by.copy()
                    tmp.append(username)
                    self.context.followed_by = tmp

                    response['status'] = 'ok'
                    response['msg'] = 'added'
                else:
                    response['status'] = 'ok'
                    response['msg'] = 'added'

            elif data['action'] == 'remove':
                if username in self.context.followed_by:
                    tmp = self.context.followed_by.copy()
                    tmp.remove(username)
                    self.context.followed_by = tmp

                    response['status'] = 'ok'
                    response['msg'] = 'removed'
                else:

                    response['status'] = 'ok'
                    response['msg'] = 'not in'
            
            else:
                response['status'] = 'error'
                response['msg'] = 'wrong method'
                
            # returns
            response['data']['followers'] = tmp
            response['data']['count'] = len(tmp)
            return response

        except Exception as e:
            return {
                'status': 'error',
                'msg': str(e),
                'data':
                {
                    'followers': tmp,
                    'count': len(tmp)
                }
            }