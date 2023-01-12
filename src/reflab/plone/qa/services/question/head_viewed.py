# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.api import user as user_api

import logging


logger = logging.getLogger("Plone")


class ViewedHead(Service):
    def reply(self):
        username = user_api.get_current().getUserName()
        if self.context.Creator() != username:
            viewed_by = self.context.viewed_by
            if username not in viewed_by :
                viewed_by.append(username)
                setattr(self.context, 'viewed_by', viewed_by)
                self.context.reindexObject(idxs=['view_count'])
        logger.info(f'User {username} viewed {self.context.absolute_url()}')
        return self.reply_no_content()
