from playground.nodes import SelfParsingNode
from django import template
from django.db.models import get_model


register = template.Library()


class GetContentTag(SelfParsingNode):

    def _get_tags(self):
        return ['as', 'for', 'limit']

    def render_content(self, tags, context):
        self.model = get_model(*self._for.split('.'))
        if self.model is None:
            raise template.TemplateSyntaxError("Generic content tag got invalid model: %s" % model)
        query_set = self.model._default_manager.all()
        context[self._as] = list(query_set[:self._limit])


get_content_tag = GetContentTag()

register.tag('sweet_get_content_tag', get_content_tag)
