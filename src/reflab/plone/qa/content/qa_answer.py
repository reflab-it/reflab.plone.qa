# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from plone.supermodel.directives import fieldset


from reflab.plone.qa import _


class IQaAnswer(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaAnswer
    """

    fieldset( 'main', label=u'Body', fields=('text', 'author', 'added_at') )
    fieldset( 'delete', label=u'Delete', fields=('deleted', 'deleted_at', 'deleted_by'))
    fieldset( 'lock', label=u'Lock', fields=('locked', 'locked_at', 'locked_by'))

    text = schema.Text( title=_(u'Text'), required=True )
    author = schema.TextLine( title=_(u'Author'), required=False )
    added_at = schema.Datetime( title =_(u'Added At'),required=False )
    approved = schema.Bool( title=_(u'Approved'), required=False )
    deleted = schema.Bool( title=_(u'Deleted'), required=False )
    deleted_at = schema.Datetime( title =_(u'Deleted at'),required=False )
    deleted_by = schema.Datetime( title =_(u'Deleted by'),required=False )
    locked = schema.Bool( title=_(u'Locked'), required=False )
    locked_at = schema.Datetime( title =_(u'Locked at'),required=False )
    locked_by = schema.TextLine( title=_(u'Locked by'), required=False )



@implementer(IQaAnswer)
class QaAnswer(Container):
    """ Content-type class for IQaAnswer
    """
