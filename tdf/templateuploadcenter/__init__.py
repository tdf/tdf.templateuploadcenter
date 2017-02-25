from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('tdf.templateuploadcenter')

MULTISPACE = u'\u3000'


def quote_chars(value):
    # We need to quote parentheses when searching text indices
    if '(' in value:
        value = value.replace('(', '"("')
    if ')' in value:
        value = value.replace(')', '")"')
    if MULTISPACE in value:
        value = value.replace(MULTISPACE, ' ')
    return value
