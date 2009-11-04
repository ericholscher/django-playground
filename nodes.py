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


class ClassBasedTag(template.Node):
    """
    Tag that combined parsing and rendering

    Subclasses should define ``render_content()`` and ``parse_content()``.

    """

    def render(self, context):
        self.context = context
        return self.render_content(context)

    def __call__(self, parser, token):
        self.token = token
        self.parser = parser
        self.parsed = self.parse_content(parser, token)
        return self

    def parse_content(self, parser, token):
        """
        This is called to parse the incoming context.
        """
        raise NotImplementedError

    def render_content(self, context):
        """
        This is called to return a node to the template.

        It should return set things in the context or return
        whatever representation is appropriate for the template.
        """
        raise NotImplementedError

class OldGetContentTag(ClassBasedTag):

    def parse_content(self, parser, token):
        bits = token.split_contents()
        if len(bits) != 4:
            raise template.TemplateSyntaxError("'%s' tag takes four arguments" % bits[0])
        if bits [2] != 'as':
            raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
        return (bits[1], 1, bits[3])

    def render_content(self, context):
        model, pk, varname = self.parsed
        self.pk = template.Variable(pk)
        self.varname = varname
        self.model = get_model(*model.split('.'))
        if self.model is None:
            raise template.TemplateSyntaxError("Generic content tag got invalid model: %s" % model)
        context[self.varname] = self.model._default_manager.get(pk=self.pk.resolve(context))


get_content_tag = GetContentTag()


class SelfParsingTag(ClassBasedTag):

    def __init__(self, required_tags=[]):
        if not required_tags:
            self.required_tags = self._get_tags()
        else:
            self.required_tags = required_tags

    def _get_tags(self):
        return []

    def parse_content(self, parser, token):
        parsed = parse_ttag(token, self.required_tags)
        for tag, val in parsed.items():
            setattr(self, '_' + tag, val)

    def render_content(self, context):
        raise NotImplementedError



class SimpleContextTag(SelfParsingTag):
    def render_content(self, tags, context):
        for tag in self.required_tags:
            print "Updating %s:%s" % (tag, tags[tag])
            context.update({tag: tags[tag]})

class GetContentTag(SelfParsingTag):
    def render_content(self, context):
        self.model = get_model(*self._for.split('.'))
        if self.model is None:
            raise template.TemplateSyntaxError("Generic content tag got invalid model: %s" % model)
        query_set = self.model._default_manager.all()
        context[self._as] = list(query_set[:self._limit])
