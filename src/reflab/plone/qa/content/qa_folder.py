# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from reflab.plone.qa import _
from zope import schema
from zope.interface import implementer, Interface
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from plone.autoform import directives
from plone.supermodel import model
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from z3c.relationfield.schema import RelationChoice
from plone.app.multilingual.browser.interfaces import make_relation_root_path

class ITagRowSchema(Interface):

    uid = schema.TextLine(
        title=u'uid',
        required=False,
    )

    name = schema.TextLine(
        title=u'name',
        required=False,
    )

    description = schema.Text(
        title=u'description',
        required=False,
    )

    popular = schema.Bool(
        title=u'popular',
        required=False,
        default=False,
    )


class IQaFolder(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaFolder
    """

    text = RichText(
        title=_(u'Text'),
        required=False
    )

    datagrid_tags = schema.List(
        title=u'Allowed Tags',
        value_type=DictRow(title=u'Tags', schema=ITagRowSchema),
        default=[],
        required=False,
    )
    directives.widget('datagrid_tags', DataGridFieldFactory)

    related_user_settings = RelationChoice(
        title=u"Users settings folder",
        vocabulary='plone.app.vocabularies.Catalog',
        required=False,
    )
    directives.widget(
        "related_user_settings",
        RelatedItemsFieldWidget,
        pattern_options={
            "selectableTypes": ["qa Settings Folder"],
            "basePath": make_relation_root_path,
        },
    )


@implementer(IQaFolder)
class QaFolder(Container):
    """ Content-type class for IQaFolder
    """
