# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from reflab.plone.qa import _
from zope import schema
from zope.interface import implementer


class IQaFolder(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaFolder
    """

    text = RichText(
        title=_(u'Text'),
        required=False
    )

    allowed_tags = schema.List(
        title=u'Allowed Tags',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )


@implementer(IQaFolder)
class QaFolder(Container):
    """ Content-type class for IQaFolder
    """
