import logging
import time

from functools import wraps
from io import StringIO
from plone.api import content as content_api
from plone.api import user as user_api
from markdown import Markdown
from Products.CMFPlone.browser.search import BAD_CHARS, quote, quote_chars
from plone.i18n.normalizer import idnormalizer


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
        raise KeyError('User folder alredy exists')

    user_folder = content_api.create(
        settings_folder, 'qa User Settings',
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
