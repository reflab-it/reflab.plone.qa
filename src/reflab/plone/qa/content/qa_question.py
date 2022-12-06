# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield import RichText
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from reflab.plone.qa import _
from z3c.form.browser.textarea import TextAreaWidget
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import implementer

from .qa_answer import IQaAnswer
from .qa_comment import IQaComment


def make_relation_root_path(context):
    return u'/'.join(context.getPhysicalPath())


class IQaQuestion(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaQuestion
    """

    fieldset(
        'activity',
        label=u'Activity',
        fields=('creators', 'approved_answer',
                'followed_by', 'voted_up_by',
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
    directives.widget('text', TextAreaWidget)

    subjects = schema.Tuple(
        title=_(u'label_tags', default=u'Tags'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )
    directives.widget(
        'subjects',
        AjaxSelectFieldWidget,
        vocabulary='reflab.plone.qa.vocabularies.question_subjects'  # TODO
    )

    # Reviewer fields
    approved_answer = RelationChoice(
        title=u"Approved Answer",
        vocabulary='reflab.plone.qa.vocabularies.question_answers',
        required=False,
    )

    directives.widget(approved_answer=SelectFieldWidget)

    directives.read_permission(creators='cmf.ReviewPortalContent')
    directives.write_permission(creators='cmf.ReviewPortalContent')
    directives.widget(
        'creators',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Users'
    )

    creators = schema.Tuple(
        title=_('label_qa_question_creators', 'Author'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
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

    # TODO share interface / behaviour with answer
    def voted_up_count(self):
        return len(self.voted_up_by)

    def voted_down_count(self):
        return len(self.voted_down_by)

    def points(self):
        return self.voted_up_count() - self.voted_down_count()

    def commment_count(self, states=['published']):
        count = 0
        for id, item in self.contentItems():
            if IQaComment.providedBy(item):
                if api.content.get_state(item) in states:
                    count += 1
        return count

    def last_activity(self):
        result = {
            'at': self.created(),
            'by': self.Creator(),
            'what': 'question'
        }

        def _check(obj):
            if result['at'] is None or result['at'] < obj.created():
                result['at'] = obj.created()
                result['by'] = obj.Creator()
                if IQaComment.providedBy(obj):
                    result['what'] = 'comment'
                if IQaAnswer.providedBy(obj):
                    result['what'] = 'answer'

        for id, item in self.contentItems():
            if IQaComment.providedBy(item):
                _check(item)
            if IQaAnswer.providedBy(item):
                _check(item)
                for id2, item2 in item.contentItems():
                    if IQaComment.providedBy(item2):
                        _check(item2)

        return result

    @property
    def last_activity_at(self):
        return self.last_activity()['at']

    @property
    def last_activity_by(self):
        return self.last_activity()['by']

    @property
    def last_activity_what(self):
        return self.last_activity()['what']

    @property
    def has_approved_answer(self):
        return True if (self.approved_answer and self.approved_answer.to_object) else False

    def _get_subjects(self):
        return self.subject

    def _set_subjects(self, value):
        self.subject = value

    subjects = property(_get_subjects, _set_subjects)
