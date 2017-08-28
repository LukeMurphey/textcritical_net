from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper
from django.template.context import RequestContext, Context
from django.template import loader, TemplateDoesNotExist
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.conf import settings

import json
import logging
import math
import difflib
import re
import os

from reader.models import Work, WorkAlias, Division, Verse, Author, RelatedWork, WikiArticle
from reader.language_tools.greek import Greek
from reader import language_tools
from reader.shortcuts import string_limiter, uniquefy, ajaxify, cache_page_if_ajax
from reader.utils import get_word_descriptions
from reader.contentsearch import search_verses, search_stats, GreekVariations
from reader.language_tools import normalize_unicode
from reader.bookcover import makeCoverImage

# Try to import the ePubExport but be forgiving if the necessary dependencies do not exist
try:
    from reader.ebook import ePubExport, MobiConvert
except ImportError:
    # Cannot import ePubExport and MobiConvert, this means we won't be able to make ebook files
    ePubExport = None
    MobiConvert = None

JSON_CONTENT_TYPE = "application/json" # Per RFC 4627: http://www.ietf.org/rfc/rfc4627.txt

# Get an instance of a logger
logger = logging.getLogger(__name__)

# These times are for making the caching decorators clearer
minutes = 60
hours   = 60 * minutes
days    = 24 * hours
months  = 30 * days
years   = 365.25 * days

@cache_page(8 * hours)
def home(request):
    greek_works_count = Work.objects.filter(language="Greek").count()
    english_works_count = Work.objects.filter(language="English").count()
    
    return render_to_response('home.html',
                              {'greek_works_count'   : greek_works_count,
                               'english_works_count' : english_works_count},
                              context_instance=RequestContext(request))

@cache_page(8 * hours)
def about(request):
    
    return render_to_response('about.html',
                              { 'title' : 'About TextCritical.net'},
                              context_instance=RequestContext(request)) 

@cache_page(8 * hours)
def contact(request):
    
    return render_to_response('contact.html',
                              { 'title' : 'Contact Us'},
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
        
    if 'include_related' in request.GET:
        search_related_forms = (request.GET['include_related'] == '1')
    else:
        search_related_forms = False
        
    if 'ignore_diacritics' in request.GET:
        ignore_diacritics = (request.GET['ignore_diacritics'] == '1')
    else:
        ignore_diacritics = False
    
    return render_to_response('search.html',
                              {'title'   : 'Search',
                               'authors' : authors,
                               'works'   : works,
                               'query'   : query,
                               'page'    : page,
                               'search_related_forms' : search_related_forms,
                               'ignore_diacritics' : ignore_diacritics
                               },
                              context_instance=RequestContext(request)) 

@cache_page(2 * hours)
def works_index(request):
    
    if 'search' in request.GET:
        search_filter = request.GET['search']
    else:
        search_filter = None
    
    return render_to_response('works_index.html',
                             {'title' : 'Works',
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

def has_numbered_book_number(division_name):
    
    if division_name is None:
        return None
    
    r = re.compile("([1-9])( .*)")
    if r.match(division_name):
        return True
    else:
        return False
    
def has_lettered_book_number(division_name):
    
    if division_name is None:
        return None
    
    r = re.compile("([IV]+)( .*)")
    if r.match(division_name):
        return True
    else:
        return False

def convert_to_lettered_division_name(division_name):
    
    if division_name is None:
        return None
    
    number_to_letter_map = {
                        '1' : 'I',
                        '2' : 'II',
                        '3' : 'III',
                        '4' : 'IV',
                        '5' : 'V'
                        }
    
    r = re.compile("([1-9])( .*)")
    m = r.match(division_name)
    
    if m and m.groups()[0] in number_to_letter_map:
        converted_character = number_to_letter_map[m.groups()[0]]
        
        return converted_character + m.groups()[1]
    else:
        return division_name

def convert_to_numbered_division_name(division_name):
    
    if division_name is None:
        return None
    
    letter_to_number_map = {
                        'I' : '1',
                        'II' : '2',
                        'III' : '3',
                        'IV' : '4',
                        'V' : '5'
                        }
    
    r = re.compile("([IV]+)( .*)")
    m = r.match(division_name)
    
    if m and m.groups()[0] in letter_to_number_map:
            
        converted_character = letter_to_number_map[m.groups()[0]]
        
        return converted_character + m.groups()[1]
    else:
        return division_name
        
def get_division( work, division_0=None, division_1=None, division_2=None, division_3=None, try_to_match_converting_numbering=True ):
    """
    This function gets the division that is associated with the given descriptor set.
    
    Arguments:
    work -- The work to get the division from
    division_0 -- The highest division to lookup
    division_1 -- The next highest division to lookup
    division_2 -- The next highest division to lookup
    division_3 -- The next highest division to lookup
    try_to_match_converting_numbering -- If not none, then attempt get a match by normalizing the division name
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
        
        if try_to_match_converting_numbering and (has_numbered_book_number(division_0) or has_numbered_book_number(division_1) or has_numbered_book_number(division_2) or has_numbered_book_number(division_3)):
            return get_division(work, convert_to_lettered_division_name(division_0), convert_to_lettered_division_name(division_1), convert_to_lettered_division_name(division_2), convert_to_lettered_division_name(division_3), try_to_match_converting_numbering=False)
        elif try_to_match_converting_numbering and (has_lettered_book_number(division_0) or has_lettered_book_number(division_1) or has_lettered_book_number(division_2) or has_lettered_book_number(division_3)):
            return get_division(work, convert_to_numbered_division_name(division_0), convert_to_numbered_division_name(division_1), convert_to_numbered_division_name(division_2), convert_to_numbered_division_name(division_3), try_to_match_converting_numbering=False)
        
        return None # We couldn't find a matching division, perhaps one doesn't exist with the given set of descriptors?
    
def download_work(request, title=None,):
    
    if 'refresh' in request.GET and request.GET['refresh'].strip().lower() in ["1", "true", "t", "", None]:
        use_cached = False
    else:
        use_cached = True
    
    # Get the format that the user is requesting
    if 'format' in request.GET:
        book_format = request.GET['format']
        
    # Ensure the format is valid
    book_format = book_format.strip().lower()
    
    mime_types = { 'epub' : 'application/epub+zip',
                   'mobi' : 'application/x-mobipocket-ebook'
                 }
    
    if book_format not in mime_types:
        raise Http404('No eBook file found for the given format')
    
    # Try to get the work
    work_alias = get_object_or_404(WorkAlias, title_slug=title)
    work = work_alias.work
    
    # Get the filename of the eBook
    ebook_file = work.title_slug + "." + book_format
    ebook_file_full_path = os.path.join( settings.GENERATED_FILES_DIR, ebook_file)
    
    # If we are using the cached file, then try to make it
    if not use_cached or not os.path.exists(ebook_file_full_path):
        
        # Make the epub. Note that we will need to make the epub even if we need to create a mobi file since mobi's are made from epub's
        if book_format == "mobi":
            epub_file_full_path = os.path.join( settings.GENERATED_FILES_DIR,  work.title_slug + ".epub" )
        else:
            epub_file_full_path = ebook_file_full_path
        
        # Stop if we don't have the ability to produce ebook files
        if ePubExport is None:
            raise Http404('eBook file not found')
            
        # Generate the ebook
        fname = ePubExport.exportWork(work, epub_file_full_path)
        
        logger.info("Created epub, filename=%s", fname)
        
        # If we need to make a mobi file, do it now
        if book_format == "mobi":
            
            # Stop if we don't have the ability to produce mobi files
            if MobiConvert is None:
                raise Http404('eBook file not found')
            
            # Generate the ebook
            fname = MobiConvert.convertEpub(work, epub_file_full_path, ebook_file_full_path)
            
            if os.path.exists(ebook_file_full_path):
                logger.info("Created mobi, filename=%s", fname)
            else:
                logger.info("Failed to create mobi, filename=%s", fname)
                raise Http404('eBook file not found')
    
    # Stream the file from the disk
    wrapper = FileWrapper(file(ebook_file_full_path))
    
    response = HttpResponse(wrapper, content_type=mime_types[book_format])
    response['Content-Disposition'] = 'attachment; filename="%s"' % (ebook_file)
    response['Content-Length'] = os.path.getsize(ebook_file_full_path)
    return response

@cache_page(8 * hours)
def work_image(request, title=None, **kwargs):

    # Try to get the work
    work_alias = get_object_or_404(WorkAlias, title_slug=title)
    work = work_alias.work

    width = None

    if 'width' in request.GET:
        width = int(request.GET['width'])

    cover_image_full_path = makeCoverImage(work, width=width)

    # Stream the file from the disk
    wrapper = FileWrapper(file(cover_image_full_path))

    response = HttpResponse(wrapper, content_type='image/png')
    response['Content-Length'] = os.path.getsize(cover_image_full_path)
    return response

@cache_page_if_ajax(12 * months, 'read_work')
@ajaxify
def read_work(request, author=None, language=None, title=None, division_0=None, division_1=None, division_2=None, division_3=None, division_4=None, leftovers=None, **kwargs):

    # Some warnings that should be posted to the user
    warnings = []
    
    # Try to get the work
    work_alias = get_object_or_404(WorkAlias, title_slug=title)
    work = work_alias.work
    
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
    
    # Get the amount of progress (based on chapters within this book)
    total_chapters_in_book = None
    completed_chapters_in_book = None
    remaining_chapters_in_book = None
    progress_in_book = None
    
    if chapter.parent_division is not None:
        total_chapters_in_book = Division.objects.filter(parent_division=chapter.parent_division, readable_unit=True).count()
        completed_chapters_in_book = Division.objects.filter(parent_division=chapter.parent_division, readable_unit=True, sequence_number__lte=chapter.sequence_number).count()
        remaining_chapters_in_book = total_chapters_in_book - completed_chapters_in_book
        progress_in_book = ((1.0 * completed_chapters_in_book ) / total_chapters_in_book) * 100
    
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
    
    # Get related works
    related_works_tmp = RelatedWork.objects.filter(work=work)#.values_list('related_work__title_slug', flat=True)
    related_works = []
    
    # Filter out entries for related works that do not have the related section
    for r in related_works_tmp:
        
        # Make up the list of chapter division descriptors
        args = []
        
        next_division = chapter
    
        while next_division is not None:
            args.insert(0, next_division.descriptor)
            next_division = next_division.parent_division
            
        # Insert the first argument (the related work)
        args.insert(0, r.related_work)
        
        # Try to get the related division
        related_work_division = get_division(*args)
        
        # If we got a match, then the link to the related work should function.
        if related_work_division is not None:
            related_works.append(r.related_work)
            
    
    # Make the chapter title
    title = work.title
    
    # Add the chapter
    chapter_description = chapter.get_division_description()
    title = title + " " + chapter_description
    
    # Add the verse
    if verse_to_highlight:
        
        if chapter_description.find(".") >= 0:
            title = title + "."
        else:
            title = title + ":"
            
        title = title + verse_to_highlight
    
    response = render_to_response('read_work.html',
                                 {'title'                      : title,
                                  'work_alias'                 : work_alias,
                                  'warnings'                   : warnings,
                                  'work'                       : work,
                                  'related_works'              : related_works,
                                  'verses'                     : verses,
                                  'divisions'                  : divisions,
                                  'chapter'                    : chapter,
                                  'chapters'                   : chapters,
                                  'authors'                    : work.authors.filter(meta_author=False),
                                  'next_chapter'               : next_chapter,
                                  'previous_chapter'           : previous_chapter,
                                  'verse_to_highlight'         : verse_to_highlight,
                                  'total_chapters'             : total_chapters,
                                  'completed_chapters'         : completed_chapters,
                                  'remaining_chapters'         : remaining_chapters,
                                  'chapter_not_found'          : chapter_not_found,
                                  'verse_not_found'            : verse_not_found,
                                  'progress'                   : progress,
                                  'progress_in_book'           : progress_in_book,
                                  'total_chapters_in_book'     : total_chapters_in_book,
                                  'completed_chapters_in_book' : completed_chapters_in_book,
                                  'remaining_chapters_in_book' : remaining_chapters_in_book
                                  },
                                  context_instance=RequestContext(request))
    
    # If the verse could not be found, set a response code to note that we couldn't get the content that the user wanted so that caching doesn't take place
    if verse_not_found:
        response.status_code = 210
        
    return response

@cache_page(8 * hours)
def robots_txt(request):
    return render_to_response('robots.txt',
                              context_instance=RequestContext(request))
    
@cache_page(8 * hours)
def humans_txt(request):
    
    try:
        version_info = loader.get_template('VERSION.txt').render()
    except TemplateDoesNotExist:
        version_info = None
    
    
    return render_to_response('humans.txt',
                              {'version_info': version_info},
                              context_instance=RequestContext(request))
    
def not_found_404(request):
    
    template = loader.get_template('404.html')
    context = Context({'title': 'Not Found'})
        
    return HttpResponse(content=template.render(context), content_type='text/html; charset=utf-8', status=404)

def tests(request):
    return render_to_response('test.html',
                              {'title'               : 'Tests',
                               'include_default_css' : 0},
                              context_instance=RequestContext(request))
    
@cache_page(8 * hours)
def beta_code_converter(request):
    return render_to_response('beta_code_converter.html',
                              {'title'               : 'Beta-code Converter'},
                              context_instance=RequestContext(request))

@cache_page(8 * hours)
def word_forms(request):
    return render_to_response('word_forms.html',
                              {'title'               : 'Word forms'},
                              context_instance=RequestContext(request))
    
# -----------------------------------
# API views are defined below
# -----------------------------------
def render_api_response(request, content, status=200):
    
    # For XML, see: http://code.activestate.com/recipes/577268-python-data-structure-to-xml-serialization/
    raw_content = json.dumps(content)
    
    return HttpResponse(raw_content, content_type=JSON_CONTENT_TYPE, status=status)

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
def api_works_typeahead_hints(request):
    
    hints = []
    
    # Get the names of works
    for work in Work.objects.all().values('title', 'title_slug'):
        hints.append( {
                       'desc': work['title'],
                       'url': reverse('read_work', args=[work['title_slug']])
                       } )
        
    #hints.extend( Work.objects.all().values_list('title', flat=True) )
    
    # Get the author names
    for author in uniquefy(Author.objects.all().values_list('name', flat=True)):
        hints.append( {
                       'desc': author,
                       'url': ''
                       } )
    #hints.extend( Author.objects.all().values_list('name', flat=True) )
    
    # Uniquefy the list
    #hints = uniquefy(hints)
    
    # Return the results
    return render_api_response(request, hints)

@cache_page(15 * minutes)
def api_search_stats(request, search_text=None ):
    
    # Get the text to search for
    if search_text is not None and len(search_text) > 0:
        pass
    elif 'q' in request.GET:
        search_text = request.GET['q']
    else:
        return render_api_error(request, "No search query was provided", 400)
    
    # Normalize the query string
    search_text = language_tools.normalize_unicode(search_text)
        
    # Determine if the related forms ought to be included
    if 'related_forms' in request.GET:
        try:
            include_related_forms = bool( int(request.GET['related_forms']) )
        except ValueError:
            include_related_forms = False
    else:
        include_related_forms = False
        
    # Determine if the diacritics ought to be ignored
    if 'ignore_diacritics' in request.GET:
        try:
            ignore_diacritics = bool( int(request.GET['ignore_diacritics']) )
        except ValueError:
            ignore_diacritics = False
    else:
        ignore_diacritics = False
        
    stats = search_stats(search_text, include_related_forms=include_related_forms, ignore_diacritics=ignore_diacritics)
    
    return render_api_response(request, stats)
    

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
        
    # Determine if the diacritics ought to be ignored
    if 'ignore_diacritics' in request.GET:
        try:
            ignore_diacritics = bool( int(request.GET['ignore_diacritics']) )
        except ValueError:
            ignore_diacritics = False
    else:
        ignore_diacritics = False
    
    # Perform the search
    search_results = search_verses( search_text, page=page, pagelen=pagelen, include_related_forms=include_related_forms, ignore_diacritics=ignore_diacritics )
    
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
    
    # Get the search stats
    stats = search_stats( search_text, include_related_forms=include_related_forms, ignore_diacritics=ignore_diacritics )
    
    results_set = {
                   'result_count' : search_results.result_count,
                   'page' : search_results.page,
                   'page_len' : search_results.pagelen,
                   'results'  : results_lists,
                   'matched_terms' : stats['matched_terms'],
                   'matched_terms_verses' : search_results.matched_terms,
                   'matched_terms_no_diacritics' : search_results.matched_terms_no_diacritics,
                   'match_count' : stats['matches'],
                   'matched_sections' : search_results.matched_sections,
                   'matched_works' : stats['matched_works']
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
def api_word_forms(request, word=None):
    
    if word is None or len(word) == 0 and 'word' in request.GET:
        word = request.GET['word']
    
    d = {}
    messages = []
    
    d['forms'] = GreekVariations.get_variations(word, include_beta_code=True, include_alternate_forms=True, ignore_diacritics=False, messages=messages)
    d['messages'] = messages
    
    return render_api_response(request, d)

@cache_page(15 * minutes)
def api_unicode_to_betacode(request, text=None):
    
    if text is None or len(text) == 0 and 'text' in request.GET:
        text = request.GET['text']
    
    d = {}
    
    d['unicode'] = text
    d['beta-code'] = Greek.unicode_to_beta_code(text)
    
    return render_api_response(request, d)

@cache_page(15 * minutes)
def api_beta_code_to_unicode(request, text=None):
    
    if text is None or len(text) == 0 and 'text' in request.GET:
        text = request.GET['text']
    
    d = {}
    
    d['unicode'] = Greek.beta_code_to_unicode(text)
    d['beta-code'] = text
    
    return render_api_response(request, d)

@cache_page(15 * minutes)
def api_works_list_for_author(request, author):
    return api_works_list(request, author)

@cache_page(4 * hours)
def api_works_list(request, author=None):
    
    # Get the relevant works
    if author is not None:
        works = Work.objects.filter(authors__name=author)
    else:
        works = Work.objects.all()
    
    # Prefetch the authors and editors, sort the results so that the response is consistent
    works = works.order_by("title").prefetch_related('authors').prefetch_related('editors')
    
    # Make the resulting JSON
    works_json = []
    
    for work in works:
        
        works_json.append( { 
                            'title' : work.title,
                            'title_slug' : work.title_slug,
                            'language' : work.language,
                            'author' : ", ".join(work.authors.values_list('name', flat=True)),
                            'editor' : ", ".join(work.editors.values_list('name', flat=True)),
                            } )
    
    return render_api_response(request, works_json)

def assign_divisions(ref_components):

    division_0, division_1, division_2, division_3, division_4 = None, None, None, None, None
    
    if len(ref_components) >= 5:
        division_0, division_1, division_2, division_3, division_4 = ref_components[:5]
    elif len(ref_components) == 4:
        division_0, division_1, division_2, division_3 = ref_components
    elif len(ref_components) == 3:
        division_0, division_1, division_2 = ref_components
    elif len(ref_components) == 2:
        division_0, division_1 = ref_components
    elif len(ref_components) == 1:
        division_0 = ref_components[0]
        
    return division_0, division_1, division_2, division_3, division_4

def swap_slugs(divisions_with_spaces, *args):
    
    results = []
    
    for arg in args:
        if arg is not None:
            for d in divisions_with_spaces:
                arg = arg.replace( slugify(d['descriptor']), d['descriptor'])
                
        results.append(arg)
        
    return results

def parse_reference_and_get_division_and_verse(regex, escaped_ref, work, divisions_with_spaces):
    
    # Try parsing the reference normally
    division_0, division_1, division_2, division_3, division_4 = assign_divisions(re.split(regex, escaped_ref))
    
    # Swap back the slugs
    division_0, division_1, division_2, division_3, division_4 = swap_slugs(divisions_with_spaces, division_0, division_1, division_2, division_3, division_4)
    
    # Try to resolve the division
    division, verse_to_highlight = get_division_and_verse(work, division_0, division_1, division_2, division_3, division_4)
    
    return division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4

def get_wikipedia_info(topic):
    import sys
    sys.path.append("lib")
    
    import wikipedia
    from wikipedia import PageError, DisambiguationError
    
    # See if an article is listed for this search term
    topic_override = WikiArticle.get_wiki_article(topic)
    
    if topic_override is not None:
        topic = topic_override
    
    # Get the wiki article
    try:
        wiki_page = wikipedia.page(topic)
        
        content = {
                   'summary': wiki_page.summary,
                   'title': wiki_page.title,
                   'url': wiki_page.url,
                   'content': wiki_page.content,
                   'links': wiki_page.links,
                   'searched_for': topic
                   }
        
        return content
    except PageError:
        return None
    except DisambiguationError:
        return None
        
    return None
    
@cache_page(4 * hours)
def api_wikipedia_info(request, topic=None, topic2=None, topic3=None):
    
    topics = []
    
    # Get the topic from the arguments
    if topic is None and 'topic' in request.GET:
        topics.append(request.GET['topic'])
    elif topic is not None:
        topics.append(topic)
        
    if topic2 is None and 'topic2' in request.GET:
        topics.append(request.GET['topic2'])
    elif topic2 is not None:
        topics.append(topic2)
        
    if topic3 is None and 'topic3' in request.GET:
        topics.append(request.GET['topic3'])
    elif topic3 is not None:
        topics.append(topic3)
        
    import sys
    sys.path.append("lib")
    
    import wikipedia
    from wikipedia import PageError, DisambiguationError
    
    # See if an article is listed for this search term
    for t in topics:
        topic_override = WikiArticle.get_wiki_article(t)
    
        if topic_override is not None:
            break
        
    # Use the topic from the wiki article list if we got one
    if topic_override is not None:
        topics.insert(0, topic_override)
    else:
        logger.info("Failed to find wiki article for topics=%r", ",".join(topics))
    
    # Get the wiki article
    for t in topics:
        content = get_wikipedia_info(t)
        
        if content is not None:
            return render_api_response(request, content)
    
    # Couldn't find the article
    return render_api_response(request, {'topic': topic}, status=404 )

def api_resolve_reference(request, work=None, ref=None):
    
    # Get the work and reference from the arguments
    if work is None and 'work' in request.GET:
        work = request.GET['work']
        
    if ref is None and 'ref' in request.GET:
        ref = request.GET['ref']
    
    # Get the work that is being referred to
    work_alias = get_object_or_404(WorkAlias, title_slug=work)
    
    # Get the division names that have spaces in them
    divisions_with_spaces = Division.objects.filter(work=work_alias.work, descriptor__contains=' ').values('descriptor')
    
    # Start making the arguments the we need for making the URL
    args = [work_alias.work.title_slug]
    
    # Swap out the titles of the divisions with spaces in the name with the title slug (we will swap them back when we are done)
    escaped_ref = ref + ''
    
    for d in divisions_with_spaces:
        escaped_ref = escaped_ref.replace(d['descriptor'], slugify(d['descriptor']))
    
    # Try to resolve the division
    division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4 = parse_reference_and_get_division_and_verse('[ .:]+', escaped_ref, work_alias.work, divisions_with_spaces)
    
    # If parsing it normally didn't parse right, then try without using the period as a separator
    if division is None and division_0 is not None:
        division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4 = parse_reference_and_get_division_and_verse('[ :]+', escaped_ref, work_alias.work, divisions_with_spaces)
        
    l = [division_0, division_1, division_2, division_3, division_4]
        
    args.extend( [x for x in l if x is not None] )
    
    return render_api_response(request, { 'url' : reverse('read_work', args=args), 'verse_to_highlight' : verse_to_highlight } )