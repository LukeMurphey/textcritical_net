from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template.context import RequestContext

import json
import logging
import math
from reader.models import Work, Division, Verse

JSON_CONTENT_TYPE = "application/json" # Per RFC 4627: http://www.ietf.org/rfc/rfc4627.txt

# Get an instance of a logger
logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('home.html',
                              {},
                              context_instance=RequestContext(request))

def works_index(request):
    
    works = Work.objects.all()
    
    return render_to_response('works_index.html',
                             {'works' : works},
                              context_instance=RequestContext(request))
    
def get_chapter_for_division(division):
    """
    Get the division that contains the next part of readable content.
    """
    
    divisions = Division.objects.filter(work=division.work, readable_unit=True, sequence_number__gte=division.sequence_number).order_by("sequence_number")[:1]
    
    if len(divisions) > 0:
        return divisions[0]
    
def get_chapters_list( division, count=9):
    
    pages_before = math.ceil( (count - 1.0) / 2 )
    pages_after = math.floor( (count - 1.0) / 2 )
    
    # Filter down the list to ones within the given work that are readable units
    divisions = Division.objects.filter(work=division.work, readable_unit=True)
    
    # Filter down the list to those in the same parent division
    if division.parent_division is not None:
        divisions = divisions.filter(parent_division=division.parent_division)
    
    # Get the number of pages before
    divisions_before = divisions.filter(sequence_number__lte=division.sequence_number).order_by("-sequence_number")[:pages_before]
    
    divisions_after = divisions.filter(sequence_number__gt=division.sequence_number).order_by("sequence_number")[:pages_after]
    
    final_list = []
    final_list.extend(divisions_before)
    final_list.reverse()
    final_list.extend(divisions_after)
    
    return final_list
    
def read_work(request, author=None, language=None, title=None, chapter=None, sub_division=None, **kwargs):
    
    # Get the verse to highlight (if provided)
    verse_to_highlight = request.GET.get('verse', None)
    
    # Try to get the work
    work = Work.objects.filter(title_slug=title)[0]
    
    # Get the chapter
    if chapter is not None:
        division = Division.objects.filter(work=work, sequence_number=chapter)[0]
    else:
        division = Division.objects.filter(work=work)[0]
    
    chapter = get_chapter_for_division(division)
    
    # Get the verses to display
    verses = Verse.objects.filter(division=chapter).all()
    
    # Get the divisions that ought to be included in the table of contents
    divisions = Division.objects.filter(work=work, readable_unit=False)
    
    if len(divisions) == 0:
        divisions = None
    
    # Get the list of chapters for pagination
    chapters = get_chapters_list(chapter)
    
    # Get the next and previous chapter number
    previous_chapter = Division.objects.filter(work=work, readable_unit=True, sequence_number__lt=chapter.sequence_number).order_by('-sequence_number').values('sequence_number')[:1]
    next_chapter = Division.objects.filter(work=work, readable_unit=True, sequence_number__gt=chapter.sequence_number).order_by('sequence_number').values('sequence_number')[:1]
    
    if len(previous_chapter) > 0:
        previous_chapter = previous_chapter[0]['sequence_number']
    else:
        previous_chapter = None
        
    if len(next_chapter) > 0:
        next_chapter = next_chapter[0]['sequence_number']
    else:
        next_chapter = None
    
    return render_to_response('read_work.html',
                             {'title'                : work.title,
                              'work'                 : work,
                              'verses'               : verses,
                              'divisions'            : divisions,
                              'chapter'              : chapter,
                              'chapters'             : chapters,
                              'next_chapter'         : next_chapter,
                              'previous_chapter'     : previous_chapter,
                              'verse_to_highlight'   : verse_to_highlight},
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