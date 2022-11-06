
from plone.app.vocabularies.metadatafields import _FIELD_LABEL
from plone.indexer.decorator import indexer

from . import _
from .content.qa_question import IQaQuestion

# This for having a translation in the collections
_FIELD_LABEL['total_question_answers'] = _('Total question answers')
_FIELD_LABEL['voted_up_count'] = _('Votes up')
_FIELD_LABEL['voted_down_count'] = _('Votes down')
_FIELD_LABEL['points'] = _('Points')


@indexer(IQaQuestion)
def total_question_answers(object, **kw):
    return object.answer_count(states=['published'])


