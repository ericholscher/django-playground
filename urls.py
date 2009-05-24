from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
     url(r'^$', 'playground.views.index', name='playground_index'),
     url(r'tag/(?P<tag>.*)/', 'playground.views.tag', name='playground_tag'),
     url(r'filter/(?P<filter>.*)/', 'playground.views.filter', name='playground_filter'),
     url(r'render/$', 'playground.views.render_template', name='playground_render'),
)
