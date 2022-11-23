from markdown import Markdown
from io import StringIO


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
