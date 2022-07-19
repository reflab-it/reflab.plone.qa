# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DatetimeFieldWidget
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

    fieldset(
        'metadata',
        label=u'Metadata',
        fields=('creators', 'tags')
    
    )
    fieldset(
        'points',
        label=u'Points',
        fields=('view_count', 'favourite_count', 'answer_count', 'points')
    )

    fieldset('activity', label=u'Activity', fields=('last_activity_at',
        'last_activity_by', 'followed_by', 'favorited_by', 'closed_by'))
    fieldset('score', label=u'Scoring System', fields=('vote_up_list', 'vote_down_list',
        'viewed_by'))


    # User fields
    title = schema.TextLine(
        title=_('label_qa_question_title', default='Question'),
        required=True
    )

    text = schema.Text(
        title=_('label_qa_question_text', default='Question details'), 
        required=False 
    )

    # Metadata: hidden for user editable by reviewers
    directives.read_permission(creators='cmf.ReviewPortalContent')
    directives.write_permission(creators='cmf.ReviewPortalContent')
    directives.widget(
        'creators',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Users'
    )    
    creators = schema.Tuple(
        title=_('label_qa_question_creators', 'Authors'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )    

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

    viewed_by = schema.List(
        title=u'Viewed By',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

@implementer(IQaQuestion)
class QaQuestion(Container):
    """ Content-type class for IQaQuestion
    """
