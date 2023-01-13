from plone import api
from plone.memoize import ram
from time import time
from Products.CMFPlone.utils import human_readable_size
from Products.CMFCore.WorkflowCore import WorkflowException

from ..helpers import get_user_settings
from ..helpers import can_user_delete
from ..helpers import can_user_answer
from ..helpers import can_user_comment
from ..helpers import can_user_vote
from ..helpers import is_question_open
from ..vocabularies import QuestionSubjectsVocabularyFactory
from ..content.qa_answer import IQaAnswer


def _user_fields_cachekey(method, username, qa_folder_uid):
    cache_time = str(time() // (60 * 60))  # 60 minutes
    return (username, qa_folder_uid, cache_time)


@ram.cache(_user_fields_cachekey)
def _cached_user_fields(username, qa_folder_uid):
    fallback = username.split('@')[0]
    result = {
        'fullname': fallback,
        'id': ''
    }
    api.env.adopt_roles(roles=['Manager'])
    qa_folder = api.content.get(UID=qa_folder_uid)
    if qa_folder is None:
        return result

    us = get_user_settings(username, qa_folder)
    if us:
        display_name = getattr(us, 'display_name', None) or fallback
        result['fullname'] = display_name.split('@')[0]
        result['id'] = us.UID()
    else:
        plone_user = api.user.get(username=username)
        if plone_user:
            fullname = plone_user.getProperty('fullname', '')
            lastname = plone_user.getProperty('lastname', '')
            if fullname or lastname:
                result['fullname'] = ' '.join([fullname, lastname])
    return result


def get_user_fields(username, qa_folder):
    qa_folder_uid = qa_folder.UID()
    return _cached_user_fields(username, qa_folder_uid)


def get_question_fields(item, is_preview=False):

    # A brute way to manage both brain and real objects...
    if hasattr(item, 'getObject'):
        obj = item.getObject()
    else:
        obj = item
        item = None

    qa_folder = obj.aq_parent
    author = obj.creators and obj.creators[0] or 'REMOVED USER'
    approved_answer = obj.approved_answer.to_object if obj.approved_answer else None

    subjects_vocabulary = QuestionSubjectsVocabularyFactory(obj)
    tags = []
    for tag in obj.subjects:
        if tag in subjects_vocabulary:
            term = subjects_vocabulary.getTerm(tag)
            tags.append({
                'id': term.value,
                'name': term.title
            })

    result = {
        '@id': obj.absolute_url(),
        'id': obj.id,
        'title': obj.title,
        'description': item and item.Description or '',  # The description is from the brain only
        'author': get_user_fields(author, qa_folder),
        'approved': approved_answer and True or False,
        'approved_answer_user': {},
        'subs': obj.answer_count(),
        'added_at': obj.created() and obj.created().asdatetime().isoformat() or '1976-04-29',
        'closed_at': None,
        'view_count': obj.view_count(),
        'comment_count': obj.commment_count(),
        'vote_count': obj.points(),
        'tags': tags,
        'is_open': is_question_open(obj),
        'can_answer': can_user_answer(obj),
        'can_comment': can_user_comment(obj),
        'can_vote': can_user_vote(obj),
        'message': obj.message,
    }

    if item is not None:
        result['last_activity'] = {
            'at': item.last_activity_at.asdatetime().isoformat() if item.last_activity_at else None,
            'by': get_user_fields(item.last_activity_by, qa_folder) if item.last_activity_by else None,
            'what': item.last_activity_what if item.last_activity_what else None,
        }
    elif obj is not None:
        result['last_activity'] = obj.last_activity()
        result['last_activity']['at'] = result['last_activity']['at'].asdatetime().isoformat() if result['last_activity']['at'] else None
        result['last_activity']['by'] = get_user_fields(result['last_activity']['by'], qa_folder) if result['last_activity']['by'] else None

    result['has_activity'] = result['last_activity']['what'] in ['comment', 'answer']

    if not result['is_open']:
        workflow_tool = api.portal.get_tool('portal_workflow')
        try:
            with api.env.adopt_roles(roles=['Manager']):
                review_history = workflow_tool.getInfoFor(obj, "review_history")
        except WorkflowException:
            review_history = []

        if review_history:
            last_transition_time = review_history[-1]['time']
            result['closed_at'] = last_transition_time.asdatetime().isoformat()
        else:
            # Fallback if not workflow history
            result['closed_at'] = result.get('last_activity', {}).get('at', None)


    if result['approved']:
        approved_answer_username = approved_answer.creators and approved_answer.creators[0] or 'REMOVED USER'
        result['approved_answer_user'] = get_user_fields(approved_answer_username, qa_folder)

    if not is_preview:
        result['text'] = obj.text and obj.text.output_relative_to(obj) or ''
        result['vote_up_count'] = obj.voted_up_count()
        result['vote_down_count'] = obj.voted_down_count()
        result['voted_up_by'] = []
        result['voted_down_by'] = []
        result['can_delete'] = can_user_delete(obj)
        result['attachments'] = []

        for attachment in obj.listFolderContents(contentFilter={"portal_type": "File"}):
            result['attachments'].append(get_attachment_fields(attachment))

    return result


def get_answer_fields(item):
    comments = [get_comment_fields(c) for c in item.listFolderContents(contentFilter={"portal_type": "qa Comment"})]
    author = item.creators and item.creators[0] or 'REMOVED USER'
    qa_folder = item.aq_parent.aq_parent
    result = {
        'id': item.id,
        'author': get_user_fields(author, qa_folder),
        'text': item.text and item.text.output_relative_to(item) or '',
        'approved': item.is_approved_answer(),
        'deleted': api.content.get_state(item) == 'deleted',
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        # 'link': item.absolute_url(),
        # 'rel': item.absolute_url(1),
        'path': f'{item.aq_parent.getId()}/{item.getId()}',
        'added_at': item.created() and item.created().asdatetime().isoformat() or '1976-04-29',
        'vote_up_count': item.voted_up_count(),
        'vote_down_count': item.voted_down_count(),
        'vote_count': item.points(),
        'comments': comments,
        'hasComments': len(comments) > 0,
        'can_delete': can_user_delete(item),
        'can_comment': can_user_comment(item),
        'can_vote': can_user_vote(item),
    }

    result['attachments'] = []

    for attachment in item.listFolderContents(contentFilter={"portal_type": "File"}):
        result['attachments'].append(get_attachment_fields(attachment))

    result['voted_up_by'] = []
    result['voted_down_by'] = []

    return result


def get_comment_fields(item):
    author = item.creators and item.creators[0] or 'REMOVED USER'
    parent = item.aq_parent
    if IQaAnswer.providedBy(parent):
        qa_folder = parent.aq_parent.aq_parent
        path = f'{parent.aq_parent.getId()}/{parent.getId()}/{item.getId()}'
    else:
        qa_folder = parent.aq_parent
        path = f'{parent.getId()}/{item.getId()}'

    return {
        'id': item.id,
        'author': get_user_fields(author, qa_folder),
        'text': item.text,
        'deleted': api.content.get_state(item) == 'deleted',
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        # 'link': item.absolute_url(),
        # 'rel': item.absolute_url(1),
        'path': path,
        'added_at': item.created() and item.created().asdatetime().isoformat() or '1976-04-29',
        'can_delete': can_user_delete(item),
    }


def get_attachment_fields(item):
    return {
        'title': item.Title(),
        'size': human_readable_size(item.get_size()),
        'filename': item.file.filename,
        'file_type': item.file.contentType,
        'url': item.absolute_url() + '/download',
        'id': item.getId()
    }
