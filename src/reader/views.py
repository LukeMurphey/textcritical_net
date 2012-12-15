from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template.context import RequestContext

import json
import logging
import math
from reader.models import Work, Division, Verse

JSON_CONTENT_TYPE = "application/json" # Per RFC 4627: http://www.ietf.org/rfc/rfc4627.txt

# Get an instance of a logger
logger = logging.getLogger(__name__)

def home(request):
    
    works_count = Work.objects.count()
    
    return render_to_response('home.html',
                              {'works_count' : works_count},
                              context_instance=RequestContext(request))

def about(request):
    
    return render_to_response('about.html',
                              {},
                              context_instance=RequestContext(request)) 

def contact(request):
    
    return render_to_response('contact.html',
                              {},
                              context_instance=RequestContext(request))

def works_index(request):
    
    works = Work.objects.all().order_by("title")
    
    if 'search' in request.GET:
        search_filter = request.GET['search']
    else:
        search_filter = None
    
    return render_to_response('works_index.html',
                             {'works' : works,
                              'filter': search_filter},
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
        
    # If no parent division was found, then filter the list down to the parent of the first division
    # so that we don't show entries for different divisions in the list
    else:
        
        # Try to get the first division
        first_division = divisions[:1]
        
        # If we got a first division, then filter on this one's parent
        if len(first_division) > 0 and first_division[0].parent_division is not None:
            divisions = divisions.filter(parent_division=first_division[0].parent_division)
        else:
            divisions = divisions.filter(parent_division=None)
    
    # Get the number of pages before
    divisions_before = divisions.filter(sequence_number__lte=division.sequence_number).order_by("-sequence_number")[:pages_before]
    
    divisions_after = divisions.filter(sequence_number__gt=division.sequence_number).order_by("sequence_number")[:pages_after]
    
    final_list = []
    final_list.extend(divisions_before)
    final_list.reverse()
    final_list.extend(divisions_after)
    
    return final_list
        
def get_division_and_verse( work, division_0=None, division_1=None, division_2=None, division_3=None, division_4=None ):
    """
    This function gets the division that is associated with the given descriptor set. If the final division descriptor is 
    actually a verse indicator, then, return the verse indicator.
    
    Arguments:
    work -- The work to get the division from
    division_0 -- The highest division to lookup
    division_1 -- The next highest division to lookup
    division_2 -- The next highest division to lookup
    division_3 -- The next highest division to lookup (this can only be a verse indicator)
    """
    
    # Assume that the descriptors are for divisions
    division = get_division( work, division_0, division_1, division_2, division_3 )
    
    if division is not None:
        return division, division_4
    
    # If we couldn't find a division, then let's assume that the last descriptor was for a verse
    if division_3 is not None:
        return get_division( work, division_0, division_1, division_2 ), division_3
    
    elif division_2 is not None:
        return get_division( work, division_0, division_1 ), division_2
    
    elif division_1 is not None:
        return get_division( work, division_0 ), division_1
    
    elif division_0 is not None:
        return get_division( work ), division_0
        
def get_division( work, division_0=None, division_1=None, division_2=None, division_3=None ):
    """
    This function gets the division that is associated with the given descriptor set.
    
    Arguments:
    work -- The work to get the division from
    division_0 -- The highest division to lookup
    division_1 -- The next highest division to lookup
    division_2 -- The next highest division to lookup
    division_3 -- The next highest division to lookup
    """
    
    # Filter down the list to the division within the given work
    divisions = Division.objects.filter(work=work)
    
    # Get the division if we got three levels deep of descriptors ("1.2.3")
    if division_0 is not None and division_1 is not None and division_2 is not None and division_3 is not None:
        
        divisions = divisions.filter(parent_division__parent_division__parent_division__parent_division=None,
                                     parent_division__parent_division__parent_division__descriptor=division_0,
                                     parent_division__parent_division__descriptor=division_1,
                                     parent_division__descriptor=division_2,
                                     descriptor=division_3)
    
    # Get the division if we got three levels deep of descriptors ("1.2.3")
    elif division_0 is not None and division_1 is not None and division_2 is not None:
        
        divisions = divisions.filter(parent_division__parent_division__parent_division=None,
                                     parent_division__parent_division__descriptor=division_0,
                                     parent_division__descriptor=division_1,
                                     descriptor=division_2)
        
    # Get the division if we got two levels deep of descriptors ("1.2")
    elif division_0 is not None and division_1:
        
        divisions = divisions.filter(parent_division__parent_division=None,
                                     parent_division__descriptor=division_0,
                                     descriptor=division_1)
    
    # Get the division if we got one level deep of descriptors ("1")
    elif division_0 is not None:
        
        divisions = divisions.filter(parent_division=None,
                                     descriptor=division_0)
    
    # Only grab one
    divisions = divisions[:1]
    
    if len(divisions) > 0:
        return divisions[0]
    else:
        return None # We couldn't find a matching division, perhaps one doesn't exist with the given set of descriptors?
    
        
def read_work(request, author=None, language=None, title=None, division_0=None, division_1=None, division_2=None, division_3=None, division_4=None, **kwargs):
    
    # Some warnings that should be posted to the user
    warnings = []
    
    # Try to get the work
    work = get_object_or_404(Work, title_slug=title)
    
    # Get the chapter
    division, verse_to_highlight = get_division_and_verse(work, division_0, division_1, division_2, division_3, division_4)
    
    # Note a warning if were unable to find the given chapter
    chapter_not_found = False
    
    if division is None and division_0 is not None:
        warnings.append( ("Section not found", "The place in the text you asked for could not be found.") )
        chapter_not_found = True
    
    # Start the user off at the beginning of the work
    if division is None:
        division = Division.objects.filter(work=work).order_by("sequence_number")[:1]
        
        if len(division) == 0:
            raise Http404('Division could not be found.')
        else:
            division = division[0]
            
    # Make sure the verse exists
    verse_not_found = False
    
    if chapter_not_found == False and verse_to_highlight is not None:
        if Verse.objects.filter(division=division, indicator=verse_to_highlight).count() == 0:
            warnings.append( ("Verse not found", "The verse you specified couldn't be found.") )
            verse_not_found = True
    
    # Get the readable unit
    chapter = get_chapter_for_division(division)
    
    # Get the verses to display
    verses = Verse.objects.filter(division=chapter).all()
    
    # Get the divisions that ought to be included in the table of contents
    divisions = Division.objects.filter(work=work, readable_unit=False)
    
    if len(divisions) == 0:
        divisions = None
    
    # Get the list of chapters for pagination
    chapters = get_chapters_list(chapter)
    
    # Get the amount of progress (based on chapters)
    total_chapters     = Division.objects.filter(work=division.work, readable_unit=True).count()
    completed_chapters = Division.objects.filter(work=division.work, readable_unit=True, sequence_number__lte=chapter.sequence_number).count()
    remaining_chapters = total_chapters - completed_chapters
    progress = ((1.0 * completed_chapters ) / total_chapters) * 100
    
    # Get the next and previous chapter number
    previous_chapter = Division.objects.filter(work=work, readable_unit=True, sequence_number__lt=chapter.sequence_number).order_by('-sequence_number')[:1]
    next_chapter = Division.objects.filter(work=work, readable_unit=True, sequence_number__gt=chapter.sequence_number).order_by('sequence_number')[:1]
    
    if len(previous_chapter) > 0:
        previous_chapter = previous_chapter[0]
    else:
        previous_chapter = None
        
    if len(next_chapter) > 0:
        next_chapter = next_chapter[0]
    else:
        next_chapter = None
    
    return render_to_response('read_work.html',
                             {'title'                : work.title,
                              'warnings'             : warnings,
                              'work'                 : work,
                              'verses'               : verses,
                              'divisions'            : divisions,
                              'chapter'              : chapter,
                              'chapters'             : chapters,
                              'authors'              : work.authors.filter(meta_author=False),
                              'next_chapter'         : next_chapter,
                              'previous_chapter'     : previous_chapter,
                              'verse_to_highlight'   : verse_to_highlight,
                              'total_chapters'       : total_chapters,
                              'completed_chapters'   : completed_chapters,
                              'remaining_chapters'   : remaining_chapters,
                              'chapter_not_found'    : chapter_not_found,
                              'verse_not_found'      : verse_not_found,
                              'progress'             : progress},
                              context_instance=RequestContext(request))

def robots_txt(request):
    return render_to_response('robots.txt',
                              context_instance=RequestContext(request))
    
def humans_txt(request):
    return render_to_response('humans.txt',
                              context_instance=RequestContext(request))
    
def not_found_404(request):
    pass
    
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