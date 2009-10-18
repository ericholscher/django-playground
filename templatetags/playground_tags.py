from playground.nodes import ParsingNode
from django import template

register = template.Library()

get_content_tag = ParsingNode(['as', 'for', 'limit'])

register.tag('sweet_get_content_tag', get_content_tag)
