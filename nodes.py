"""
Subclass of ``template.Node`` for easy context updating.

"""

from django.db.models import get_model
from django.conf import settings
from django import template

register = template.Library()


def parse_ttag(token, required_tags):
    """
    A function to parse a template tag.
    Pass in the token to parse, and a list of keywords to look for.
    It sets the name of the tag to 'tag_name' in the hash returned.

    >>> from test_utils.templatetags.utils import parse_ttag
    >>> parse_ttag('super_cool_tag for my_object as bob', ['as'])
    {'tag_name': u'super_cool_tag', u'as': u'bob'}
    >>> parse_ttag('super_cool_tag for my_object as bob', ['as', 'for'])
    {'tag_name': u'super_cool_tag', u'as': u'bob', u'for': u'my_object'}

    """

    if isinstance(token, template.Token):
        bits = token.split_contents()
    else:
        bits = token.split(' ')
    tags = {'tag_name': bits.pop(0)}
    for index, bit in enumerate(bits):
        bit = bit.strip()
        if bit in required_tags:
            if len(bits) != index-1:
                tags[bit.strip()] = bits[index+1]
    return tags


class SelfParsingNode(template.Node):
    """
    Node that updates the context with certain values.

    Subclasses should define ``get_content()``, which should return a
    dictionary to be added to the context.

    """

    def __init__(self, required_tags):
        self.required_tags = required_tags
        #self.__name__ = 'sweet_tag_' + '_'.join(required_tags)

    def render(self, context):
        self.parsed = self.parser(context)
        return self.display_content(self.parsed, context)

    def parser(self, context):
        return parse_ttag(self.token, self.required_tags)

    def display_content(self, tags, context):
        print "%s, %s" % (tags, context)
        raise NotImplementedError

    def __call__(self, parser, token):
        self.token = token
        self.parser = parser
        return self

class ParsingNode(SelfParsingNode):
    def display_content(self, tags, context):
        for tag in self.required_tags:
            print "Updating %s:%s" % (tag, tags[tag])
            context.update({tag: tags[tag]})

