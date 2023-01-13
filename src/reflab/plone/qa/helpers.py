import logging
import time

from functools import wraps
from io import StringIO
from plone.api import content as content_api
from plone.api import user as user_api
from plone.api import portal as portal_api
from markdown import Markdown
from Products.CMFPlone.browser.search import BAD_CHARS, quote, quote_chars
from plone.i18n.normalizer import idnormalizer
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import Super as BaseUnrestrictedUser

from .content.qa_answer import IQaAnswer
from .content.qa_comment import IQaComment

logger = logging.getLogger("Plone")


def _unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        _unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = _unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def markdown_to_text(markdown_string):
    # see: https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
    return __md.convert(markdown_string)


def _safe_username(username):
    return idnormalizer.normalize(username)


def _get_settings_folder(qa_folder):
    relation = getattr(qa_folder, 'related_user_settings', None)
    if not relation:
        return None

    return relation.to_object


def create_user_settings(username, qa_folder):
    settings_folder = _get_settings_folder(qa_folder)

    if settings_folder is None:
        raise KeyError('Settings folder not set')

    safe_username = _safe_username(username)
    display_name = username.split('@')[0]
    plone_user = user_api.get(username)
    if plone_user:
        fullname = plone_user.getProperty('fullname', '')
        lastname = plone_user.getProperty('lastname', '')
        if fullname or lastname:
            display_name = ' '.join([fullname, lastname])

    if safe_username in settings_folder.objectIds():
        raise KeyError('User folder already exists')

    logger.info(f'Creating user folder for: {username} with id {safe_username}')
    user_folder = execute_with_role(
        'Manager',
        content_api.create,
        settings_folder,
        'qa User Settings',
        id=safe_username,
        display_name=display_name,
        title=username
    )

    return user_folder


def get_user_settings(username, qa_folder):
    settings_folder = _get_settings_folder(qa_folder)

    if settings_folder is None:
        return None

    safe_username = _safe_username(username)

    if safe_username not in settings_folder.objectIds():
        return None

    return settings_folder[safe_username]


def munge_search_term(search_text):
    # Taken from Products/CMFPlone/browser/search.py
    # Used for search questions API
    for char in BAD_CHARS:
        search_text = search_text.replace(char, ' ')
    r = map(quote, search_text.split())
    r = " AND ".join(r)
    r = quote_chars(r) + '*'
    return r


def can_user_delete(obj):
    """ Check if a given user can delete an object """
    if IQaAnswer.providedBy(obj):
        question = obj.aq_parent
    elif IQaComment.providedBy(obj):
        if IQaAnswer.providedBy(obj.aq_parent):
            question = obj.aq_parent.aq_parent
        else:
            question = obj.aq_parent
    else:
        question = obj

    if not is_question_open(question):
        return False

    plone_user = user_api.get_current()
    username = plone_user.getUserName()

    # Only authors can delete own contents
    if obj.Creator() != username:
        return False

    # If there are subobject can't delete
    if obj.listFolderContents(contentFilter={"portal_type": ["qa Comment", "qa Answer"]}):
        return False

    # If it is a question or answer and has votes can't delete
    if obj.portal_type in ["qa Comment", "qa Answer"]:
        if obj.points() != 0:
            return False

    return True


def is_question_open(obj):
    return content_api.get_state(obj) == 'published'


def can_user_answer(obj):
    return True if is_question_open(obj) else False


def can_user_comment(obj):
    if IQaAnswer.providedBy(obj):
        question = obj.aq_parent
    else:
        question = obj
    return True if is_question_open(question) else False


def can_user_vote(obj):
    if IQaAnswer.providedBy(obj):
        question = obj.aq_parent
    else:
        question = obj
    return True if is_question_open(question) else False


def time_profiler(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__module__} - {func}: ran in {round(end - start, 4)}s")
        return result

    return wrapper


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def execute_with_role(role, function, *args, **kwargs):
    portal = portal_api.get()
    sm = getSecurityManager()
    try:
        try:
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', [role], ''
            )
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)
            return function(*args, **kwargs)
        except Exception as e:
            raise e
    finally:
        setSecurityManager(sm)
