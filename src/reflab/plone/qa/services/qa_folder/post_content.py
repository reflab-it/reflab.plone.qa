# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone import api
from plone.restapi.services import Service
from zope.interface import alsoProvides
from plone.app.textfield.value import RichTextValue
from datetime import datetime
import plone.protect.interfaces
import json
import uuid

from ...content.qa_answer import IQaAnswer
from ...helpers import can_user_answer
from ...helpers import can_user_comment


class Content(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = {"result": {"code": None, "data": None}}
        invalid_response = {"status": "error", "message": "invalid data"}
        _type = None
        _parent_type = None
        _parent_id = None
        _data_is_valid = True
        user_name = None

        post_data = self.request["BODY"] or None

        if api.user.is_anonymous() or post_data is None:
            return invalid_response

        data = {}
        response = {}
        try:
            user_name = api.user.get_current().getUserName()
            data = json.loads(post_data)
            _type = data.get("type")
            _parent_type = data.get("parent_type")
            _parent_id = data.get("parent_id")
        except Exception:
            _data_is_valid = False

        if _data_is_valid is not True:
            return invalid_response

        if _type is None or _parent_type is None or _parent_id is None:
            return invalid_response

        # check type
        if _type not in ["question", "comment", "reply"]:
            return {"status": "error", "message": "invalid type"}

        # create comment or response
        if _type == "question":
            folder = self.context
            try:
                _title = data.get("title")
                if _title is None or _title == "" or len(_title) < 3:
                    response["status"] = "error"
                    response["message"] = "unable to created, missing title"
                else:
                    res = api.content.create(
                        container=folder,
                        type="qa Question",
                        subjects=data.get("tags"),
                        title=_title,
                        creators=(user_name,),
                        added_at=datetime.now(),
                        followed_by=[user_name],
                        text=RichTextValue(
                            raw=data.get("data") or "", outputMimeType="text/plain"
                        ),
                    )

                    response["status"] = "ok"
                    response["message"] = "created"

            except Exception:
                response["status"] = "error"
                response["message"] = "unable to created"

        elif _type == "comment":
            try:
                obj = api.content.find(context=self.context, id=_parent_id)
                parent = obj[0].getObject()
                if not can_user_comment(parent):
                    raise Unauthorized("User can't add a comment")
                res = api.content.create(
                    container=parent,
                    type="qa Comment",
                    id=str(uuid.uuid4()),
                    creators=(user_name,),
                    added_at=datetime.now(),
                    text=data.get("data") or "",
                )

                if IQaAnswer.providedBy(parent):
                    question = parent.aq_parent
                else:
                    question = parent

                if user_name not in question.followed_by:
                    question.followed_by.append(user_name)

                response["status"] = "ok"
                response["message"] = "created"
            except Exception:
                response["status"] = "error"
                response["message"] = "unable to created"

        elif _type == "reply":
            # getting base object
            obj = api.content.find(context=self.context, id=_parent_id)
            question = obj[0].getObject()
            try:
                if not can_user_answer(question):
                    raise Unauthorized("User can't add an answer")
                res = api.content.create(
                    container=question,
                    type="qa Answer",
                    id=str(uuid.uuid4()),
                    creators=(user_name,),
                    added_at=datetime.now(),
                    text=RichTextValue(
                        raw=data.get("data") or "", outputMimeType="text/plain"
                    ),
                )

                if user_name not in question.followed_by:
                    question.followed_by.append(user_name)

                response["status"] = "ok"
                response["message"] = "created"
            except Exception:
                response["status"] = "error"
                response["message"] = "unable to created"

        else:
            response["status"] = "error"
            response["message"] = "unable to created, wrong type"

        response["id"] = res.id if res else None
        return response
