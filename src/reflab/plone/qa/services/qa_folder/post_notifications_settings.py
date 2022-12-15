# -*- coding: utf-8 -*-
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

from ...content.qa_user_settings import frequency_on_followed_questions_values
from ...content.qa_user_settings import frequency_on_followed_tags_values

class NotificationsSettingsPost(Service):

    def reply(self):
        # disable cors
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        invalid_response = {"status": "error", "message": "invalid data"}
        post_data = self.request["BODY"] or None

        if api.user.is_anonymous() or post_data is None:
            return invalid_response

        # collect daata
        data = json.loads(post_data)

        on_tags_frequency = data.get("on_tags_frequency") or None
        on_questions_frequency = data.get("on_questions_frequency") or None

        if on_tags_frequency is None or on_questions_frequency is None:
            return invalid_response

        # get the user
        plone_user = api.user.get_current()
        username = plone_user.getUserName()

        # Also create the user folder settings if it not exists
        qa_folder = self.context
        with api.env.adopt_roles(roles=['Manager']):
            user_settings = get_user_settings(username, qa_folder)
            if user_settings is None:
                alsoProvides(self.request, IDisableCSRFProtection)
                user_settings = create_user_settings(username, qa_folder)
            if on_tags_frequency in frequency_on_followed_tags_values \
                and on_questions_frequency in frequency_on_followed_questions_values:
                setattr(user_settings, 'notification_frequency_on_followed_tags', on_tags_frequency)
                setattr(user_settings, 'notification_frequency_on_followed_questions', on_questions_frequency)
            else:
                return invalid_response

        response = {"status": "ok", "message": ""}
        return response
