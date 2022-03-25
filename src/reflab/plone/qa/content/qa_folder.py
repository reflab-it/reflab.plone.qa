# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


from reflab.plone.qa import _


class IQaFolder(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaFolder
    """

    text = RichText(
        title=_(u'Text'),
        required=False
    )


@implementer(IQaFolder)
class QaFolder(Container):
    """ Content-type class for IQaFolder
    """
