from DateTime import DateTime

from .content.qa_question import IQaQuestion
from .content.qa_answer import IQaAnswer


def _get_parent_question(object):
    question = None
    parent = object.aq_parent

    if IQaAnswer.providedBy(parent):
        parent = parent.aq_parent

    if IQaQuestion.providedBy(parent):
        question = parent

    return question


def on_answer_added(object, event):
    question = _get_parent_question(object)
    if question:
        question.reindexObject(idxs=['last_activity_at', 'last_activity_by', 'last_activity_what', 'answer_count'])


def on_comment_added(object, event):
    question = _get_parent_question(object)
    if question:
        question.reindexObject(idxs=['last_activity_at', 'last_activity_by', 'last_activity_what', 'comment_count'])
