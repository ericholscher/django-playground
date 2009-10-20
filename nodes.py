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

    if hasattr(token, 'split_contents'):
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

    def __init__(self, required_tags=[]):
        if not required_tags:
            self.required_tags = self._get_tags()
        else:
            self.required_tags = required_tags

    def _get_tags(self):
        return []

    def render(self, context):
        self.context = context
        self.parsed = parse_ttag(self.token, self.required_tags)
        for tag, val in self.parsed.items():
            setattr(self, '_'+tag, val)
        return self.render_content(self.parsed, context)

    def __call__(self, parser, token):
        self.token = token
        self.parser = parser
        return self

    def render_content(self, tags, context):
        raise NotImplementedError


class ParsingNode(SelfParsingNode):
    def render_content(self, tags, context):
        for tag in self.required_tags:
            print "Updating %s:%s" % (tag, tags[tag])
            context.update({tag: tags[tag]})
