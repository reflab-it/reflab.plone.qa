# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from reflab.plone.qa import _
from zope import schema
from zope.interface import implementer


class IQaQuestion(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaQuestion
    """

    fieldset( 'main', label=u'Body', fields=('text', 'author', 'added_at') )
    fieldset( 'status', label=u'Status', fields=('closed', 'deleted', 'approved'))
    fieldset( 'points', label=u'Points', fields=('view_count', 'favourite_count',
        'answer_count', 'points'))
    fieldset( 'activity', label=u'Activity', fields=('last_activity_at',
        'last_activity_by', 'followed_by', 'favorited_by', 'closed_by'))

    text = schema.Text( title=_(u'Text'), required=False )
    author = schema.TextLine( title=_(u'Author'), required=False )
    added_at = schema.Datetime( title =_(u'Added At'),required=False )

    closed = schema.Bool( title=_(u'Closed'), required=False )
    deleted = schema.Bool( title=_(u'Deleted'), required=False )
    approved = schema.Bool( title=_(u'Approved'), required=False )

    view_count = schema.Int( title=_(u'view_count'), required=False )
    favourite_count = schema.Int( title=_(u'favourite_count'), required=False )
    answer_count = schema.Int( title=_(u'answer_count'), required=False )
    points = schema.Int( title=_(u'points'), required=False )

    last_activity_at = schema.Datetime( title =_(u'Last activity at'),required=False )
    last_activity_by = schema.TextLine( title=_(u'Last activity by'), required=False )
    followed_by = schema.TextLine( title=_(u'Followed by'), required=False )
    favorited_by = schema.TextLine( title=_(u'Favorited by'), required=False )
    closed_by = schema.TextLine( title=_(u'Closed by'), required=False )

    tags = schema.List(
        title=u'Tags',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

@implementer(IQaQuestion)
class QaQuestion(Container):
    """ Content-type class for IQaQuestion
    """
