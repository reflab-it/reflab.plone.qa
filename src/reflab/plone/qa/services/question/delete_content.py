# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone.restapi.services import Service
from plone.api import content as content_api
from plone.api import user as user_api
from plone.api import env as env_api
from ...helpers import can_user_delete


class ContentDelete(Service):
    """Deletes a QA content"""

    def reply(self):
        if can_user_delete(self.context):
            with env_api.adopt_roles(['Manager']):
                content_api.delete(obj=self.context, check_linkintegrity=False)

        return self.reply_no_content()
