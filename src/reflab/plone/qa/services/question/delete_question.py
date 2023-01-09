# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone.restapi.services import Service
from plone.api import content as content_api
from plone.api import user as user_api
from ...helpers import can_user_delete


class QuestionDelete(Service):
    """Deletes a question."""

    def reply(self):

        plone_user = user_api.get_current()
        username = plone_user.getUsername()

        if can_user_delete(username, self.context):
            content_api.delete(obj=self.context, check_linkintegrity=False)

        return self.reply_no_content()
