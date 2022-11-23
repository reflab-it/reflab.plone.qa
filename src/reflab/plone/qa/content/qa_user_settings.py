# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from plone.autoform import directives
from zope.interface import implementer
from plone.app.z3cform.widget import SelectFieldWidget

from .. import _
frequency_on_followed_tags_values = [u'Weekly', u'Daily', u'Never']
frequency_on_followed_questions_values = [u'Hourly', u'Never']


class IQAUserSettings(model.Schema):
    """ """

    title = schema.TextLine(
        title=_('label_qa_username', default='Username'),
        required=True
    )

    display_name = schema.TextLine(
        title=_('label_qa_user_displayname', default='Display name'),
        required=True
    )

    followed_tags = schema.List(
        title=u'Followed tags',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

    directives.widget(notification_frequency_on_followed_tags=SelectFieldWidget)
    notification_frequency_on_followed_tags = schema.Choice(
        title=u'Notification frequency on followed tags',
        values=frequency_on_followed_tags_values,
        default='Weekly',
        required=True,
    )

    directives.widget(notification_frequency_on_followed_questions=SelectFieldWidget)
    notification_frequency_on_followed_questions = schema.Choice(
        title=u'Notification frequency on followed questions',
        values=frequency_on_followed_questions_values,
        default='Hourly',
        required=True,
    )


@implementer(IQAUserSettings)
class QAUserSettings(Item):
    """ """