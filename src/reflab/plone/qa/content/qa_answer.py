# -*- coding: utf-8 -*-
from plone import api
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.textfield import RichText as RichTextField
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from reflab.plone.qa import _
from zope import schema
from zope.interface import implementer

from .qa_comment import IQaComment


class IQaAnswer(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaAnswer
    """
    fieldset(
        'activity', 
        label=u'Activity',
        fields=('creators', 'approved',  'voted_up_by', 'voted_down_by')
    )

    # User fields
    text = RichTextField(
        title=_('label_qa_answer_text', default='Text'), 
        required=True, 
        default_mime_type='text/plain',
        output_mime_type='text/plain',
        allowed_mime_types=('text/plain'),          
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
        title=_('label_qa_answer_creators', 'Authors'),
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


@implementer(IQaAnswer)
class QaAnswer(Container):
    """ Content-type class for IQaAnswer
    """

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
