# -*- coding: utf-8 -*-
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from reflab.plone.qa import _
from zope import schema
from zope.interface import implementer



class IQaComment(model.Schema):
    """ Marker interface and Dexterity Python Schema for QaComment
    """

    fieldset(
        'activity', 
        label=u'Activity',
        fields=('creators',)
    )

    # User fields
    text = schema.Text(
        title=_('label_qa_answer_text', default='Text'), 
        required=True 
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

@implementer(IQaComment)
class QaComment(Container):
    """ Content-type class for IQaComment
    """
