# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from reflab.plone.qa import _
from zope import schema
from zope.interface import implementer


class IQaAnswer(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaAnswer
    """

    fieldset( 'main', label=u'Body', fields=('text', 'author', 'added_at') )
    fieldset( 'delete', label=u'Delete', fields=('deleted', 'deleted_at', 'deleted_by'))
    fieldset( 'lock', label=u'Lock', fields=('locked', 'locked_at', 'locked_by'))
    fieldset('score', label=u'Scoring System', fields=('vote_up_list', 'vote_down_list'))

    text = schema.Text( title=_(u'Text'), required=True )
    author = schema.TextLine( title=_(u'Author'), required=False )
    added_at = schema.Datetime( title =_(u'Added At'),required=False )
    approved = schema.Bool( title=_(u'Approved'), required=False )
    deleted = schema.Bool( title=_(u'Deleted'), required=False )
    deleted_at = schema.Datetime( title =_(u'Deleted at'),required=False )
    deleted_by = schema.TextLine( title=_(u'Locked by'), required=False )
    locked = schema.Bool( title=_(u'Locked'), required=False )
    locked_at = schema.Datetime( title =_(u'Locked at'),required=False )
    locked_by = schema.TextLine( title=_(u'Locked by'), required=False )

    vote_up_list = schema.List(
        title=u'Vote Up List',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

    vote_down_list = schema.List(
        title=u'Vote Down List',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )


@implementer(IQaAnswer)
class QaAnswer(Container):
    """ Content-type class for IQaAnswer
    """
