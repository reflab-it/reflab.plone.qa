# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from reflab.plone.qa import _
from zope import schema
from plone.autoform import directives
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.multilingual.browser.interfaces import make_relation_root_path
from zope.interface import implementer


class IQASettingsFolder(model.Schema):
    """ """

    related_qa_folder = RelationChoice(
        title=u"Relationchoice field",
        vocabulary='plone.app.vocabularies.Catalog',
        required=False,
    )
    directives.widget(
        "related_qa_folder",
        RelatedItemsFieldWidget,
        pattern_options={
            "selectableTypes": ["qa Folder"],
            "basePath": make_relation_root_path,
        },
    )


@implementer(IQASettingsFolder)
class QASettingsFolder(Container):
    """ """
