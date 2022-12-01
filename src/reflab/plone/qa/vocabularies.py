from plone import api
from plone.app.vocabularies.metadatafields import _FIELD_LABEL
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form.interfaces import IDisplayForm

from . import _
from .content.qa_question import IQaQuestion
from .content.qa_folder import IQaFolder

# This for having a translation in the collections
_FIELD_LABEL['answer_count'] = _('Question answers')
_FIELD_LABEL['view_count'] = _('Question views')
_FIELD_LABEL['favorite_count'] = _('Question favorites')
_FIELD_LABEL['followed_count'] = _('Question followers')
_FIELD_LABEL['last_activity_at'] = _('Question last activity date')
_FIELD_LABEL['has_approved_answer'] = _('Question has approved answer')
_FIELD_LABEL['followed_by'] = _('Question followed by')
_FIELD_LABEL['voted_up_count'] = _('Votes up')
_FIELD_LABEL['voted_down_count'] = _('Votes down')
_FIELD_LABEL['points'] = _('Points')
_FIELD_LABEL['comment_count'] = _('Comments')
_FIELD_LABEL['voted_up_by'] = _('Voted up by')
_FIELD_LABEL['voted_down_by'] = _('Voted down by')


@implementer(IVocabularyFactory)
class QuestionAnswersVocabulary(object):
    def __call__(self, context=None):
        terms = []
        results = []

        if context and IQaQuestion.providedBy(context):
            results = api.content.find(
                portal_type='qa Answer',
                sort_on='sortable_title',
                path='/'.join(context.getPhysicalPath())
            )

        for brain in results:
            title = f'By {brain.Creator} - {brain.Title}'
            terms.append(SimpleTerm(
                value=brain.getObject(),
                token=brain.UID,
                title=title,
            ))

        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class QuestionSubjectsVocabulary(object):
    def __call__(self, context=None):
        terms = []
        qa_folder = None

        if IDisplayForm.providedBy(context):
            context = context.getContent()

        if IQaQuestion.providedBy(context):
            qa_folder = context.aq_parent

        if IQaFolder.providedBy(context):
            qa_folder = context

        if qa_folder:
            for tag in qa_folder.datagrid_tags:
                terms.append(SimpleTerm(
                    value=tag['uid'],
                    token=tag['uid'],
                    title=tag['name']
                ))

        return SimpleVocabulary(terms)


QuestionAnswersVocabularyFactory = QuestionAnswersVocabulary()
QuestionSubjectsVocabularyFactory = QuestionSubjectsVocabulary()
