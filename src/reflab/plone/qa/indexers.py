from plone.indexer import indexer

from .content.qa_answer import IQaAnswer
from .content.qa_comment import IQaComment
from .content.qa_question import IQaQuestion
from .helpers import markdown_to_text


def _md2txt(text, limit):
    if hasattr(text, 'raw'):
        text = text.raw
    text = markdown_to_text(text)
    return text[:limit] + '...' if len(text) > limit else text

@indexer(IQaQuestion)
def question_description(object):
    text = getattr(object, 'text', '')
    return _md2txt(text, 200)


@indexer(IQaAnswer)
def answer_title(object):
    text = getattr(object, 'text', '')
    return _md2txt(text, 60)


@indexer(IQaComment)
def comment_title(object):
    text = getattr(object, 'text', '')
    return _md2txt(text, 60)