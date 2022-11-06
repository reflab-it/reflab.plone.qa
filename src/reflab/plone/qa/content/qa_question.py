# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield import RichText
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from reflab.plone.qa import _
from zope import schema
from zope.interface import implementer

from .qa_answer import IQaAnswer


class IQaQuestion(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaQuestion
    """

    fieldset(
        'activity',
        label=u'Activity',
        fields=('creators', 'approved', 'last_activity_at', 'last_activity_by',
                'followed_by', 'favorited_by', 'closed_by', 'voted_up_by',
                'voted_down_by', 'viewed_by')
    )

    # User fields
    title = schema.TextLine(
        title=_('label_qa_question_title', default='Question'),
        required=True
    )

    text = RichText(
        title=_('label_qa_question_text', default='Question details'),
        required=False,
        default_mime_type='text/plain',
        output_mime_type='text/plain',
        allowed_mime_types=('text/plain'),
    )

    subjects = schema.Tuple(
        title=_(u'label_tags', default=u'Tags'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )
    directives.widget(
        'subjects',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Keywords'  # TODO
    )

    # Reviewer fields
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

    directives.read_permission(approved='cmf.ReviewPortalContent')
    directives.write_permission(approved='cmf.ReviewPortalContent')
    approved = schema.Bool(
        title=_(u'Approved'),
        required=False
    )

    directives.read_permission(last_activity_at='cmf.ReviewPortalContent')
    directives.write_permission(last_activity_at='cmf.ReviewPortalContent')
    last_activity_at = schema.Datetime(
        title=_(u'Last activity at'),
        required=False
    )

    directives.read_permission(last_activity_by='cmf.ReviewPortalContent')
    directives.write_permission(last_activity_by='cmf.ReviewPortalContent')
    last_activity_by = schema.TextLine(
        title=_(u'Last activity by'),
        required=False
    )

    directives.read_permission(followed_by='cmf.ReviewPortalContent')
    directives.write_permission(followed_by='cmf.ReviewPortalContent')
    followed_by = schema.List(
        title=_(u'Followed by'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

    directives.read_permission(favorited_by='cmf.ReviewPortalContent')
    directives.write_permission(favorited_by='cmf.ReviewPortalContent')
    favorited_by = schema.List(
        title=_(u'Favorited by'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

    directives.read_permission(closed_by='cmf.ReviewPortalContent')
    directives.write_permission(closed_by='cmf.ReviewPortalContent')
    closed_by = schema.TextLine(
        title=_(u'Closed by'),
        required=False
    )

    directives.read_permission(voted_up_by='cmf.ReviewPortalContent')
    directives.write_permission(voted_up_by='cmf.ReviewPortalContent')
    voted_up_by = schema.List(
        title=u'Voted up by',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

    directives.read_permission(voted_down_by='cmf.ReviewPortalContent')
    directives.write_permission(voted_down_by='cmf.ReviewPortalContent')
    voted_down_by = schema.List(
        title=u'Voted down by',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )

    directives.read_permission(viewed_by='cmf.ReviewPortalContent')
    directives.write_permission(viewed_by='cmf.ReviewPortalContent')
    viewed_by = schema.List(
        title=u'Viewed by',
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[],
    )


@implementer(IQaQuestion)
class QaQuestion(Container):
    """ Content-type class for IQaQuestion
    """

    def view_count(self):
        return len(self.viewed_by)

    def favourite_count(self):
        return len(self.favorited_by)

    def followed_count(self):
        return len(self.followed_by)

    def answer_count(self, states=['published']):
        count = 0
        for id, item in self.contentItems():
            if IQaAnswer.providedBy(item):
                if api.content.get_state(item) in states:
                    count += 1
        return count

    def commment_count(self):
        return len(self.listFolderContents(contentFilter={"portal_type": "qa Comment"}))

    def voted_up_count(self):
        return len(self.voted_up_by)

    def voted_down_count(self):
        return len(self.voted_down_by)

    def points(self):
        return self.voted_up_count() - self.voted_down_count()
