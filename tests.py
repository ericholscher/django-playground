from django.test import TestCase

from django.template import Context, Template
from django import template

from mock import Mock

class SimpleTest(TestCase):
    fixtures = ['test_data']
    def test_basic_self_parsing(self):
        from playground.templatetags.playground_tags import get_content_tag
        token = Mock()
        token.split_contents.return_value = ['sweet_tag', 'for', 'auth.user', 'as', 'latest_events', 'limit', '66']
        context = Context({})
        Node = get_content_tag('', token)
        Node.render(context)
        self.assertEqual(str(context.get('latest_events')), '[<User: eric>]')
