from plone import api
from plone.app.textfield.interfaces import ITransformer
from zope.interface import implementer

import re

file_regex= r"\[[^\]]*\]\((?P<filename>.*?)(?=\"|\))(?P<optionalpart>\".*\")?\)"

@implementer(ITransformer)
class QATextTransformer(object):

    """Convert the RichText value of QA Contents for images and attachments
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, value, mimeType):

        def convert_file_text(match_obj):
            filename = match_obj.group(1)
            optionalpart = match_obj.group(1)
            
            if filename is not None:
                if not filename.startswith(('http://', 'https://')):
                    _filename = filename
                    if not filename.startswith('/'):
                        _filename = '/' + filename
                    url = self.context.absolute_url() + _filename + '/download'
                    return match_obj.group().replace(filename, url)

        return re.sub(file_regex, convert_file_text, value.raw)
