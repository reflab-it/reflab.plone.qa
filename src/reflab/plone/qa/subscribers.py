from DateTime import DateTime
from datetime import datetime

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


def on_question_modified(object, event):
    # Manage the date of answer approval
    # We store the date on the question but it is also indexed on the Answer
    # to allow the creation of reports using Collections
    # The date is automatically remove when the approved answer is unset
    # The date is automatically set if the editor does not set it
    approved_answer_changed = False
    approved_date_changed = False
    for description in event.descriptions:
        if 'approved_answer' in description.attributes:
            approved_answer_changed = True
        if 'approved_date' in description.attributes:
            approved_date_changed = True

    if approved_answer_changed:
        if object.approved_answer and not object.approved_date:
            object.approved_date = datetime.now().date()
            approved_date_changed = True
        elif not object.approved_answer:
            object.approved_date = None
            approved_date_changed = True

    if not (approved_date_changed or approved_answer_changed):
        return

    # Reindex where required
    for answer in object.listFolderContents(contentFilter={"portal_type": ["qa Answer"]}):
        if approved_date_changed:
            answer.reindexObject(idxs=['approved_date'])
        if approved_answer_changed:
            answer.reindexObject(idxs=['is_approved_answer'])


def on_answer_added(object, event):
    question = _get_parent_question(object)
    if question:
        question.reindexObject(idxs=['last_activity_at', 'last_activity_by', 'last_activity_what', 'answer_count'])


def on_comment_added(object, event):
    question = _get_parent_question(object)
    if question:
        question.reindexObject(idxs=['last_activity_at', 'last_activity_by', 'last_activity_what', 'comment_count'])
