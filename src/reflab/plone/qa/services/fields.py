from plone import api

from ..helpers import get_user_settings
from ..vocabularies import QuestionSubjectsVocabularyFactory


def get_user_fields(username):
    fallback = username.split('@')[0]
    result = {
        'fullname': fallback,
        'id': ''
    }
    us = get_user_settings(username)
    if us:
        display_name = getattr(us, 'display_name', None) or fallback
        result['fullname'] = display_name
        result['id'] = us.UID()
    else:
        plone_user = api.user.get(username=username)
        if plone_user:
            fullname = plone_user.getProperty('fullname', None) or fallback
            if fullname:
                result['fullname'] = fullname
    return result


def get_question_fields(item, is_preview=False):

    # A brute way to manage both brain and real objects...
    if hasattr(item, 'getObject'):
        obj = item.getObject()
    else:
        obj = item
        item = None

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
        'author': get_user_fields(author),
        'approved': approved_answer and True or False,
        'approved_answer_user': {},
        'subs': obj.answer_count(),
        'added_at': obj.created() and obj.created().asdatetime().isoformat() or '1976-04-29',
        'view_count': obj.view_count(),
        'comment_count': obj.commment_count(),
        'vote_count': obj.points(),
        'tags': tags,
    }

    if result['approved']:
        approved_answer_username = approved_answer.creators and approved_answer.creators[0] or 'REMOVED USER'
        result['approved_answer_user'] = get_user_fields(approved_answer_username)

    if not is_preview:
        result['text'] = obj.text and obj.text.output_relative_to(obj) or ''
        result['vote_up_count'] = obj.voted_up_count(),
        result['vote_down_count'] = obj.voted_down_count(),

    return result


def get_answer_fields(item):
    comments = [get_comment_fields(c) for c in item.listFolderContents(contentFilter={"portal_type": "qa Comment"})]
    author = item.creators and item.creators[0] or 'REMOVED USER'
    return {
        'id': item.id,
        # 'title': item.title,
        # 'description': item.description,
        'author': get_user_fields(author),
        'text': item.text and item.text.output_relative_to(item) or '',
        'approved': item.UID() == item.aq_parent.approved_answer,
        'deleted': api.content.get_state(item) == 'deleted',
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        'link': item.absolute_url(),
        'rel': item.absolute_url(1),
        # 'subs': len(item.items()),
        # 'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
        'added_at': item.created() and item.created().asdatetime().isoformat() or '1976-04-29',
        # 'view_count': int(len(item.viewed_by)),
        'vote_up_count': item.voted_up_count(),
        'vote_down_count': item.voted_down_count(),
        'vote_count': item.points(),
        'comments': comments,
        'hasComments': len(comments) > 0,
    }


def get_comment_fields(item):
    author = item.creators and item.creators[0] or 'REMOVED USER'
    return {
        'id': item.id,
        # 'title': item.title,
        # 'description': item.description,
        'author': get_user_fields(author),
        'text': item.text,
        'deleted': api.content.get_state(item) == 'deleted',
        '_meta':
        {
            'type': item.Type(),
            'portal_type': item.portal_type
        },
        'link': item.absolute_url(),
        'rel': item.absolute_url(1),
        # 'last_activity_at': item.last_activity_at and item.last_activity_at.isoformat() or '1976-04-29',
        'added_at': item.created() and item.created().asdatetime().isoformat() or '1976-04-29',
        # 'view_count': int(len(item.viewed_by)),
    }