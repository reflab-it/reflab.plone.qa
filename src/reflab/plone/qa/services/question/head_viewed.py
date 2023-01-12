# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.api import user as user_api

import logging


logger = logging.getLogger("Plone")


class ViewedHead(Service):
    def reply(self):
        username = user_api.get_current().getUserName()
        logger.info(f'User {username} viewed {self.context.absolute_url()}')
        return self.reply_no_content()
