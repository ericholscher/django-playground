# Create your views here.

from django.template import Template, Context
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.core import serializers
from django.contrib.admindocs.views import load_all_installed_template_libraries
from django.contrib.admindocs import utils
from django.template.context import RequestContext
from django import template
from BeautifulSoup import BeautifulSoup
import re

def parse_ttag(token):
    bits = token.split()
    tags = {}
    possible_tags = ['as', 'for', 'limit', 'exclude']
    for index, bit in enumerate(bits):
        if bit.strip() in possible_tags:
            tags[bit.strip()] = bits[index+1]
    return tags

def context_for_object(token, Node):
    """This is a function that returns a Node.
    It takes a string from a template tag in the format
    TagName for [object] as [context variable]
    """
    tags = parse_ttag(token)
    if len(tags) == 2:
        return Node(tags['for'], tags['as'])
    elif len(tags) == 1:
        return Node(tags['for'])
    else:
        #raise template.TemplateSyntaxError, "%s: Fail" % bits[]
        print "ERROR"


def _get_tags():
    load_all_installed_template_libraries()

    tags = []
    for module_name, library in template.libraries.items():
        for tag_name, tag_func in library.tags.items():
            title, body, metadata = utils.parse_docstring(tag_func.__doc__)
            if title:
                title = utils.parse_rst(title, 'tag', ('tag:') + tag_name)
            if body:
                body = utils.parse_rst(body, 'tag', ('tag:') + tag_name)
            for key in metadata:
                metadata[key] = utils.parse_rst(metadata[key], 'tag', ('tag:') + tag_name)
            if library in template.builtins:
                tag_library = None
            else:
                tag_library = module_name.split('.')[-1]
            tags.append({
                'name': tag_name,
                'title': title,
                'body': body,
                'meta': metadata,
                'library': tag_library,
            })
    return tags

def _get_filters():
    load_all_installed_template_libraries()

    filters = []
    for module_name, library in template.libraries.items():
        for filter_name, filter_func in library.filters.items():
            title, body, metadata = utils.parse_docstring(filter_func.__doc__)
            if title:
                title = utils.parse_rst(title, 'filter', ('filter:') + filter_name)
            if body:
                body = utils.parse_rst(body, 'filter', ('filter:') + filter_name)
            for key in metadata:
                metadata[key] = utils.parse_rst(metadata[key], 'filter', ('filter:') + filter_name)
            if library in template.builtins:
                tag_library = None
            else:
                tag_library = module_name.split('.')[-1]
            filters.append({
                'name': filter_name,
                'title': title,
                'body': body,
                'meta': metadata,
                'library': tag_library,
            })
    return filters

def index(request):
    return render_to_response('playground/index.html',
                              {'tags': _get_tags() },
                              context_instance=RequestContext(request))

def tag(request, tag):
    tags = _get_tags()
    this_tag = None
    for _tag in tags:
        if _tag['name'].strip() == tag.strip():
            this_tag = _tag

    soup = BeautifulSoup(this_tag['body'])
    code = soup.find('pre')
    code = re.sub('<.*>', '', str(code), count=99)
    tag_re = re.compile('({% .* %})')
    match = tag_re.search(code)

    as_var = ""
    if match:
        __tags = parse_ttag(match.group(1))
        if 'as' in __tags:
            as_var = __tags['as']

    return render_to_response('playground/tag.html',
                              { 'tag_obj': this_tag,
                               'tags': _get_tags(),
                               'template_code': code,
                               'as_var': as_var },
                              context_instance=RequestContext(request))

def filter(request, filter):
    filters = _get_filters()
    this_filter = None
    for _filter in filters:
        if _filter['name'].strip() == filter.strip():
            this_filter = _filter

    soup = BeautifulSoup(this_filter['body'])
    code = soup.find('pre')
    code = re.sub('<.*>', '', str(code), count=99)
    filter_re = re.compile('({% .* %})')
    match = filter_re.search(code)

    as_var = ""
    if match:
        __filters = parse_tfilter(match.group(1))
        if 'as' in __filters:
            as_var = __filters['as']

    return render_to_response('playground/filter.html',
                              { 'filter_obj': this_filter,
                               'filters': _get_filters(),
                               'template_code': code,
                               'as_var': as_var },
                              context_instance=RequestContext(request))


def render_template(request):
    context = request.POST['context']
    context_dict = {}
    for line in context.split('\n'):
        try:
            name, val = line.split(':')
            context_dict[name] = val.strip()
        except: #Blank lines
            pass
    try:
        c = Context(context_dict)
        template = request.POST['template']
        t = Template(template)
        string = t.render(c)
    except Exception, e:
        string = e
    return HttpResponse(string)
