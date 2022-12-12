# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from zope.interface import alsoProvides
import plone.protect.interfaces
import json


class Follow(Service):
    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        response = {"status": "", "msg": "", "data": {}}

        # getting user by session
        username = api.user.get_current().getUserName()
        # but getting action from posted data
        post_data = self.request["BODY"] or None
        data = json.loads(post_data)
        tmp = []  # reference array

        if data["action"] == "add":
            if username not in self.context.followed_by:
                tmp = self.context.followed_by.copy()
                tmp.append(username)
                self.context.followed_by = tmp
                self.context.reindexObject(idxs=['followed_by', 'followed_count'])

                response["status"] = "ok"
                response["msg"] = "added"
            else:
                response["status"] = "ok"
                response["msg"] = "added"

        elif data["action"] == "remove":
            if username in self.context.followed_by:
                tmp = self.context.followed_by.copy()
                tmp.remove(username)
                self.context.followed_by = tmp
                self.context.reindexObject(idxs=['followed_by', 'followed_count'])

                response["status"] = "ok"
                response["msg"] = "removed"
            else:

                response["status"] = "ok"
                response["msg"] = "not in"

        else:
            response["status"] = "error"
            response["msg"] = "wrong method"

        # returns
        response["data"]["followers"] = tmp
        response["data"]["count"] = tmp
        return response

