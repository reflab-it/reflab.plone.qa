# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from plone.autoform import directives
from zope.interface import implementer
from plone.app.z3cform.widget import SelectFieldWidget

from .. import _


class IQAUserSettings(model.Schema):
    """ """

    title = schema.TextLine(
        title=_('label_qa_username', default='Username'),
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
        title=u'Notification frequency on followed types',
        values=[u'Weekly', u'Daily', u'Never'],
        default='Weekly',
        required=True,
    )

    directives.widget(notification_frequency_on_followed_questions=SelectFieldWidget)
    notification_frequency_on_followed_questions = schema.Choice(
        title=u'Notification frequency on followed questions',
        values=[u'Hourly', u'Never'],
        default='Hourly',
        required=True,
    )


@implementer(IQAUserSettings)
class QAUserSettings(Container):
    """ """
