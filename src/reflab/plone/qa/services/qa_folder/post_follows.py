# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from zope.interface import alsoProvides
from plone.app.textfield.value import RichTextValue
from datetime import datetime
import plone.protect.interfaces
import json
from plone.protect.interfaces import IDisableCSRFProtection

from ...helpers import get_user_settings
from ...helpers import create_user_settings


from ...content.qa_answer import IQaAnswer


class Follows(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = {"result": {"code": None, "data": None}}
        invalid_response = {"status": "error", "message": "invalid data"}
        _passed_tag = None
        _data_is_valid = True
        user_name = None

        post_data = self.request["BODY"] or None

        if api.user.is_anonymous() or post_data is None:
            return invalid_response

        data = {}
        response = {}
        all_valid_tags = [i['uid'] for i in self.context.datagrid_tags]
        user_name = api.user.get_current().getUserName()
        data = json.loads(post_data)
        _passed_tag = data.get("tag")
        if _passed_tag in all_valid_tags:
            qa_folder = self.context
            with api.env.adopt_roles(roles=['Manager']):
                user_settings = get_user_settings(user_name, qa_folder)
                if user_settings is None:
                    alsoProvides(self.request, IDisableCSRFProtection)
                    user_settings = create_user_settings(user_name, qa_folder)
                    followed_tags = getattr(user_settings, 'followed_tags', [])
                    if _passed_tag not in followed_tags:
                        user_settings.followed_tags.append(_passed_tag)
                        _data_is_valid = True
        if _data_is_valid is not True:
            return invalid_response

        if _passed_tag is None:
            return invalid_response

        # check if tag ids exist?
        if _data_is_valid:
            response["status"] = "ok"
            response["message"] = ""
        else:
            response["status"] = "error"
            response["message"] = "unable to created"

        return response
