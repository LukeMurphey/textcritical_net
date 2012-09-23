from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template.context import RequestContext
import json
import logging
from reader.models import Work, Chapter, Verse, Section

JSON_CONTENT_TYPE = "application/json" # Per RFC 4627: http://www.ietf.org/rfc/rfc4627.txt

# Get an instance of a logger
logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))

def works_index(request):
    
    works = Work.objects.all()
    
    return render_to_response('works_index.html',
                             {'works' : works},
                              context_instance=RequestContext(request))
    
def read_work(request, title=None, first_number=None, second_number=None, **kwargs):
    
    # Get the verse to highlight (if provided)
    verse_to_highlight = request.GET.get('verse', None)
    
    # Try to get the work
    work = Work.objects.filter(title=title)[0]
    
    # Get the chapter
    if first_number is not None:
        chapter = Chapter.objects.filter(work=work, sequence_number=first_number)[0]
    else:
        chapter = Chapter.objects.filter(work=work)[0]
    
    # Get the verses to display
    verses = Verse.objects.filter(chapter=chapter).all()
    
    # Get the sections
    sections = Section.objects.filter(chapters__work=work).distinct()
    
    if len(sections) == 0:
        sections = None
    
    # Provide the section that includes this chapter
    section = None
    
    chapter_sections = Section.objects.filter(chapters=chapter)[:1]
    
    if len(chapter_sections) > 0:
        section = chapter_sections[0]
    
    # Get the next and previous chapter number
    next_chapter = chapter.sequence_number + 1
    previous_chapter = chapter.sequence_number - 1
    
    # Determine if we should display the 
    has_previous_chapter = Chapter.objects.filter(work=work, sequence_number=previous_chapter).count() > 0
    has_next_chapter = Chapter.objects.filter(work=work, sequence_number=next_chapter).count() > 0
    
    return render_to_response('read_work.html',
                             {'title'   : work.title,
                              'work'    : work,
                              'chapter' : chapter,
                              'verses'  : verses,
                              'sections': sections,
                              'section' : section,
                              'has_next_chapter' : has_next_chapter,
                              'has_previous_chapter' : has_previous_chapter,
                              'next_chapter' : next_chapter,
                              'previous_chapter' : previous_chapter,
                              'verse_to_highlight': verse_to_highlight},
                              context_instance=RequestContext(request))

def robots_txt(request):
    return render_to_response('robots.txt',
                              context_instance=RequestContext(request))
    
def humans_txt(request):
    return render_to_response('humans.txt',
                              context_instance=RequestContext(request))
    
    
# -----------------------------------
# API views are defined below
# -----------------------------------
def render_api_response(request, content):
    
    # For XML, see: http://code.activestate.com/recipes/577268-python-data-structure-to-xml-serialization/
    raw_content = json.dumps(content)
    
    return HttpResponse(raw_content, content_type=JSON_CONTENT_TYPE)

def api_index(request):
    
    urls = []
    
    def make_url( url_list, name ):
        url_list.append( {"path" : reverse(name), "name" : name } )
    
    make_url(urls, "api_index")
    make_url(urls, "api_beta_code_to_unicode")
    
    return render_api_response(request, urls)

def api_beta_code_to_unicode(request):
    
    return HttpResponse("Not implemented yet", content_type=JSON_CONTENT_TYPE)

def api_works_list(request):
    
    response = HttpResponse(content_type=JSON_CONTENT_TYPE)
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(Work.objects.all(), stream=response)