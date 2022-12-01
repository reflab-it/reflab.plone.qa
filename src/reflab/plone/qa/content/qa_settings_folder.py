# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from reflab.plone.qa import _
from zope import schema
from plone.autoform import directives
from plone.supermodel import model
from zope.interface import implementer


class IQASettingsFolder(model.Schema):
    """ """


@implementer(IQASettingsFolder)
class QASettingsFolder(Container):
    """ """
