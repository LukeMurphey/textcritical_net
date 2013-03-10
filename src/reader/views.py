from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.core.cache import cache

import json
import logging
import math
import difflib
import re

from reader.models import Work, Division, Verse, Author
from reader.language_tools.greek import Greek
from reader import language_tools
from reader.shortcuts import string_limiter, uniquefy
from reader.utils import get_word_descriptions
from reader.contentsearch import search_verses
from reader.language_tools import normalize_unicode

JSON_CONTENT_TYPE = "application/json" # Per RFC 4627: http://www.ietf.org/rfc/rfc4627.txt

# Get an instance of a logger
logger = logging.getLogger(__name__)

# These times are for making the caching decorators clearer
minutes = 60
hours   = 60 * minutes
days    = 24 * hours
months  = 30 * days
years   = 365.25 * days

@cache_page(15 * minutes)
def home(request):
    greek_works_count = Work.objects.filter(language="Greek").count()
    english_works_count = Work.objects.filter(language="English").count()
    
    return render_to_response('home.html',
                              {'greek_works_count'   : greek_works_count,
                               'english_works_count' : english_works_count},
                              context_instance=RequestContext(request))

def about(request):
    
    return render_to_response('about.html',
                              {},
                              context_instance=RequestContext(request)) 

def contact(request):
    
    return render_to_response('contact.html',
                              {},
                              context_instance=RequestContext(request))

def search(request, query=None):
    
    authors = Author.objects.all().order_by("name")
    works = Work.objects.all().order_by("title")
    
    if 'q' in request.GET:
        query = request.GET['q']
    else:
        query = None
        
    if 'page' in request.GET:
        page = request.GET['page']
    else:
        page = None
    
    return render_to_response('search.html',
                              {'authors' : authors,
                               'works'   : works,
                               'query'   : query,
                               'page'    : page
                               },
                              context_instance=RequestContext(request)) 

@cache_page(8 * hours)
def works_index(request):
    
    works = Work.objects.all().order_by("title").prefetch_related('authors').prefetch_related('editors')
    
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
    """
    Get the list of chapters for pagination.
    """
    
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
                                     parent_division__parent_division__parent_division__descriptor__iexact=division_0,
                                     parent_division__parent_division__descriptor__iexact=division_1,
                                     parent_division__descriptor__iexact=division_2,
                                     descriptor=division_3)
    
    # Get the division if we got three levels deep of descriptors ("1.2.3")
    elif division_0 is not None and division_1 is not None and division_2 is not None:
        
        divisions = divisions.filter(parent_division__parent_division__parent_division=None,
                                     parent_division__parent_division__descriptor__iexact=division_0,
                                     parent_division__descriptor__iexact=division_1,
                                     descriptor=division_2)
        
    # Get the division if we got two levels deep of descriptors ("1.2")
    elif division_0 is not None and division_1:
        
        divisions = divisions.filter(parent_division__parent_division=None,
                                     parent_division__descriptor__iexact=division_0,
                                     descriptor=division_1)
    
    # Get the division if we got one level deep of descriptors ("1")
    elif division_0 is not None:
        divisions = divisions.filter(parent_division=None,
                                     descriptor__iexact=division_0)
        
    
    # Only grab one
    divisions = divisions[:1]
    
    if len(divisions) > 0:
        return divisions[0]
    else:
        return None # We couldn't find a matching division, perhaps one doesn't exist with the given set of descriptors?
    
@cache_page(8 * hours)
def read_work(request, author=None, language=None, title=None, division_0=None, division_1=None, division_2=None, division_3=None, division_4=None, leftovers=None, **kwargs):
    
    # Some warnings that should be posted to the user
    warnings = []
    
    # Try to get the work
    work = get_object_or_404(Work, title_slug=title)
    
    # Get the chapter
    division, verse_to_highlight = get_division_and_verse(work, division_0, division_1, division_2, division_3, division_4)
    
    # Note a warning if were unable to find the given chapter
    chapter_not_found = False
    
    if leftovers is not None:
        warnings.append( ("Section not found", "The place in the text you asked for could not be found (the reference you defined is too deep).") )
        chapter_not_found = True
    
    elif division is None and division_0 is not None:
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

@cache_page(8 * hours)
def robots_txt(request):
    return render_to_response('robots.txt',
                              context_instance=RequestContext(request))
    
@cache_page(8 * hours)
def humans_txt(request):
    return render_to_response('humans.txt',
                              context_instance=RequestContext(request))
    
def not_found_404(request):
    pass

def tests(request):
    return render_to_response('test.html',
                              {'include_default_css' : 0},
                              context_instance=RequestContext(request))
    
# -----------------------------------
# API views are defined below
# -----------------------------------
def render_api_response(request, content):
    
    # For XML, see: http://code.activestate.com/recipes/577268-python-data-structure-to-xml-serialization/
    raw_content = json.dumps(content)
    
    return HttpResponse(raw_content, content_type=JSON_CONTENT_TYPE)

def render_api_error(request, message, status=400):
    
    content = { 'message' : message }
    
    raw_content = json.dumps(content)
    
    return HttpResponse(raw_content, content_type=JSON_CONTENT_TYPE, status=status)

def render_queryset_api_response(request, content):
    
    response = HttpResponse(content_type=JSON_CONTENT_TYPE)
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(content, stream=response, indent=2)
    
    return response

def api_index(request):
    
    urls = []
    
    def make_url( url_list, name ):
        url_list.append( {"path" : reverse(name), "name" : name } )
    
    make_url(urls, "api_index")
    make_url(urls, "api_beta_code_to_unicode")
    make_url(urls, "api_works_list")
    
    return render_api_response(request, urls)

def description_id_fun(x):
    """
    Provides the string necessary to uniquefy WordDescription instances.
    
    Arguments:
    x -- a word description instance.
    """
    
    return str(x)

@cache_page(1 * hours)
def api_works_typehead_hints(request ):
    
    hints = []
    
    # Get the names of works
    hints.extend( Work.objects.all().values_list('title', flat=True) )
    
    # Get the author names
    hints.extend( Author.objects.all().values_list('name', flat=True) )
    
    # Uniquefy the list
    hints = uniquefy(hints)
    
    # Return the results
    return render_api_response(request, hints)

@cache_page(15 * minutes)
def api_search(request, search_text=None ):
    
    # Get the text to search for
    if search_text is not None and len(search_text) > 0:
        pass
    elif 'q' in request.GET:
        search_text = request.GET['q']
    else:
        return render_api_error(request, "No search query was provided", 400)
    
    # Normalize the query string
    search_text = language_tools.normalize_unicode(search_text)
    
    # Get the page number
    if 'page' in request.GET:
        try:
            page = int(request.GET['page'])
        except ValueError:
            page = 1
    else:
        page = 1
    
    # Get the page length
    if 'pagelen' in request.GET:
        try:
            pagelen = int(request.GET['pagelen'])
        except ValueError:
            pagelen = 10
    else:
        pagelen = 10
        
    # Determine if the related forms ought to be included
    if 'related_forms' in request.GET:
        try:
            include_related_forms = bool( int(request.GET['related_forms']) )
        except ValueError:
            include_related_forms = False
    else:
        include_related_forms = False
    
    # Perform the search
    search_results = search_verses( search_text, page=page, pagelen=pagelen, include_related_forms=include_related_forms )
    
    # This will be were the results are stored
    results_lists = []
    
    # Prepare the results
    for result in search_results.verses:
        
        d = {}
        
        # Build the list of arguments necessary to make the URL
        args = [ result.verse.division.work.title_slug ]
        args.extend( result.verse.division.get_division_indicators() )
        
        # Determine if the last verse is a lone verse. If it is, then don't put the verse in the URL args.
        if Verse.objects.filter(division=result.verse.division).count() > 1:
            division_has_multiple_verses = True
            args.append( str(result.verse) )
        else:
            division_has_multiple_verses = False
        
        d['url']             = reverse('read_work', args=args )
        d['verse']           = str(result.verse)
        d['division']        = result.verse.division.get_division_description()
        d['work_title_slug'] = result.verse.division.work.title_slug
        d['work']            = result.verse.division.work.title
        d['highlights']      = result.highlights
        d['content_snippet'] = string_limiter(result.verse.content, 80)
        
        # If the verse is not a lone verse (has other verses next to it under the parent division) then add the verse information to the list
        if division_has_multiple_verses:
            
            if '.' in d['division']:
                d['description'] = d['division'] + "." + d['verse']
            else:
                d['description'] = d['division'] + ":" + d['verse']
                
        # If the verse is a lone verse, don't bother adding it
        else:
            d['description'] = d['division']
        
        # Append the results
        results_lists.append(d)
    
    results_set = {
                   'result_count' : search_results.result_count,
                   'page' : search_results.page,
                   'page_len' : search_results.pagelen,
                   'results'  : results_lists
                   }
    
    
    # Return the results
    return render_api_response(request, results_set)

@cache_page(15 * minutes)
def api_convert_query_beta_code(request, search_query):
    
    if search_query is None or len(search_query) == 0 and 'q' in request.GET:
        search_query = request.GET['q']
        
    # Break up the query into individual search strings
    
    queries = search_query.split(" ")
    
    # convert all items that
    beta_fields = ["content", "no_diacritics", "section", None]
    
    # This will be the new search string
    new_queries = []
    
    for q in queries:
        
        # By default, assume that the query is unchanged
        new_q = q
        
        # If the query has the field specified, then separate it
        if ":" in q:
            field, value = re.split("[:]", q, 1)
                    
        # If the query has no field, then set the field to none
        else:
            field = None
            value = q
            
        # If the field is for a field that can contain beta-code, then convert it
        if field in beta_fields:
            
            # Add the field to the query if it exists
            if field is not None:
                new_q = field + ":"
            else:
                new_q = ""
                
            # Add and convert the field
            if re.match("\w+", value ):
                # If is just ASCII, then convert it
                new_q = new_q + Greek.beta_code_to_unicode(value)
            else:
                # Otherwise, don't. It may be Greek already
                new_q = new_q + value
            
        # Add the query to the list
        new_queries.append(new_q) 
            
    return render_api_response(request, " ".join(new_queries) )

@cache_page(15 * minutes)
def api_word_parse(request, word=None):
    
    if word is None or len(word) == 0 and 'word' in request.GET:
        word = request.GET['word']
    
    word_basic_form = language_tools.strip_accents( normalize_unicode(word) )
    
    # Do a search for the parse
    ignoring_diacritics = False
    ignoring_numerals = False
    descriptions = get_word_descriptions( word, False )
    
    # If we couldn't find the word, then try again ignoring diacritical marks
    if len(descriptions) == 0:
        ignoring_diacritics = True
        descriptions = get_word_descriptions( word, True )
        
    # If we couldn't find the word and it has numbers (indicating a particular parse, then remove the numbers and try again)
    if len(descriptions) == 0 and re.search("[0-9]", word) is not None:
        
        # Strip the numbers
        stripped_word = normalize_unicode(re.sub("[0-9]", "", word))
        
        ignoring_numerals = True
        
        # Try without ignoring diacritics
        ignoring_diacritics = False
        descriptions = get_word_descriptions( stripped_word, False )
        
        # Try with ignoring diacritics
        if len(descriptions) == 0:
            ignoring_diacritics = True
            descriptions = get_word_descriptions( stripped_word, True )
    
    # Make the final result to be returned
    results = []
    
    for d in descriptions:
        
        entry = {}
        
        entry["meaning"] = d.meaning
        entry["description"] = str(d)
        entry["ignoring_numerals"] = ignoring_numerals
        entry["ignoring_diacritics"] = ignoring_diacritics
        entry["form"] = d.word_form.form
        
        if d.lemma:
            entry["lemma"] = d.lemma.lexical_form
        else:
            entry["lemma"] = None
            
        # Calculate the similarity so that sort the results by similarity
        entry["similarity"] = int(round(difflib.SequenceMatcher(None, entry["lemma"], word_basic_form).ratio() * 100, 0))
        
        results.append(entry)
        
    # If we are ignoring diacritics, then sort the entries by the similarity
    def word_compare(x, y):
        return y["similarity"] - x["similarity"]
    
    results = sorted(results, cmp=word_compare)
    
    # Return the response
    return render_api_response(request, results)

@cache_page(15 * minutes)
def api_word_parse_beta_code(request, word=None):
    
    if word is None or len(word) == 0 and 'word' in request.GET:
        word = request.GET['word']
    
    return api_word_parse(request, Greek.beta_code_to_unicode(word))

@cache_page(15 * minutes)
def api_unicode_to_betacode(request, word=None):
    if word is None or len(word) == 0 and 'word' in request.GET:
        word = request.GET['word']
    
    d = {}
    
    d['unicode'] = word
    d['beta-code'] = Greek.unicode_to_beta_code(word)
    
    return render_api_response(request, d)

@cache_page(15 * minutes)
def api_beta_code_to_unicode(request, word=None):
    
    if word is None or len(word) == 0 and 'word' in request.GET:
        word = request.GET['word']
    
    d = {}
    
    d['unicode'] = Greek.beta_code_to_unicode(word)
    d['beta-code'] = word
    
    return render_api_response(request, d)

@cache_page(15 * minutes)
def api_works_list_for_author(request, author):
    
    works = Work.objects.filter(authors__name=author)
    
    results = []
    
    for work in works:
        result = {}
        result['title'] = work.title
        result['title_slug'] = work.title_slug
        
        results.append(result)
    
    return render_api_response(request, results)

@cache_page(15 * minutes)
def api_works_list(request):
    
    response = HttpResponse(content_type=JSON_CONTENT_TYPE)
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(Work.objects.all(), stream=response)
    
    return response