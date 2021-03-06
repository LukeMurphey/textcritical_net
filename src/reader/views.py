from django.shortcuts import get_object_or_404, render
from django.urls import NoReverseMatch
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from wsgiref.util import FileWrapper
from django.template.context import RequestContext
from django.template import loader, TemplateDoesNotExist
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.cache import patch_response_headers
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from functools import cmp_to_key

import json
import logging
import difflib
import re
import os

from reader.templatetags.reader_extras import transform_perseus_text
from reader.models import Work, WorkAlias, Division, Verse, Author, RelatedWork, WikiArticle, LexiconEntry, WorkSource
from reader.language_tools.greek import Greek
from reader import language_tools
from reader.shortcuts import string_limiter, uniquefy, convert_xml_to_html5
from reader.utils import get_word_descriptions
from reader.contentsearch import search_verses, search_stats, GreekVariations
from reader.language_tools import normalize_unicode
from reader.bookcover import makeCoverImage
from reader.utils.work_helpers import get_division_and_verse, get_chapter_for_division, get_chapters_list, get_division, get_work_page_info

# Try to import the ePubExport but be forgiving if the necessary dependencies do not exist
try:
    from reader.ebook import ePubExport, MobiConvert
except ImportError:
    # Cannot import ePubExport and MobiConvert, this means we won't be able to make ebook files
    ePubExport = None
    MobiConvert = None

# Per RFC 4627: http://www.ietf.org/rfc/rfc4627.txt
JSON_CONTENT_TYPE = "application/json"

# Get an instance of a logger
logger = logging.getLogger(__name__)

# These times are for making the caching decorators clearer
minutes = 60
hours = 60 * minutes
days = 24 * hours
months = 30 * days
years = 365.25 * days


def single_page_app(request, **kwargs):
    return render(request, 'spa.html',
                  {},
                  RequestContext(request))


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

    mime_types = {'epub': 'application/epub+zip',
                  'mobi': 'application/x-mobipocket-ebook'
                  }

    if book_format not in mime_types:
        raise Http404('No eBook file found for the given format')

    # Try to get the work
    work_alias = get_object_or_404(WorkAlias, title_slug=title)
    work = work_alias.work

    # Make the directory
    if not os.path.isdir(settings.GENERATED_FILES_DIR):
        os.mkdir(settings.GENERATED_FILES_DIR)

    # Get the filename of the eBook
    ebook_file = work.title_slug + "." + book_format
    ebook_file_full_path = os.path.join(
        settings.GENERATED_FILES_DIR, ebook_file)

    # If we are using the cached file, then try to make it
    if not use_cached or not os.path.exists(ebook_file_full_path):

        # Make the epub. Note that we will need to make the epub even if we need to create a mobi file since mobi's are made from epub's
        if book_format == "mobi":
            epub_file_full_path = os.path.join(
                settings.GENERATED_FILES_DIR,  work.title_slug + ".epub")
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
            fname = MobiConvert.convertEpub(
                work, epub_file_full_path, ebook_file_full_path)

            if os.path.exists(ebook_file_full_path):
                logger.info("Created mobi, filename=%s", fname)
            else:
                logger.info("Failed to create mobi, filename=%s", fname)
                raise Http404('eBook file not found')

    # Stream the file from the disk
    wrapper = FileWrapper(open(ebook_file_full_path, 'rb'))

    response = HttpResponse(wrapper, content_type=mime_types[book_format])
    response['Content-Disposition'] = 'attachment; filename="%s"' % (
        ebook_file)
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

    try:
        cover_image_full_path = makeCoverImage(work, width=width)

        # Stream the file from the disk
        wrapper = FileWrapper(open(cover_image_full_path, 'rb'))

        response = HttpResponse(wrapper, content_type='image/png')
        response['Content-Length'] = os.path.getsize(cover_image_full_path)
        return response
    except Exception as e:
        logger.exception(
            "Failed to create the work image, work=%r", work.title_slug)
        response = HttpResponse("Image could not be created.")
        response.status_code = 500
        return response


@cache_page(8 * hours)
def robots_txt(request):
    return render(request, 'robots.txt',
                  {},
                  RequestContext(request))


@cache_page(8 * hours)
def humans_txt(request):
    try:
        version_info = loader.get_template('VERSION.txt').render()
    except TemplateDoesNotExist:
        version_info = None

    return render(request, 'humans.txt',
                  {'version_info': version_info},
                  RequestContext(request))


def not_found_404(request, *args, **kwargs):
    return render(request, 'spa.html',
                  {},
                  RequestContext(request),
                  status=404)


def error_500(request, *args, **kwargs):
    return render(request, 'spa.html',
                  {},
                  RequestContext(request),
                  status=500)

# -----------------------------------
# API views are defined below
# -----------------------------------


def render_api_response(request, content, status=200, cache_timeout=None):

    # For XML, see: http://code.activestate.com/recipes/577268-python-data-structure-to-xml-serialization/
    raw_content = json.dumps(content)

    response = HttpResponse(
        raw_content, content_type=JSON_CONTENT_TYPE, status=status)

    if cache_timeout is not None:
        patch_response_headers(response, cache_timeout)

    return response


def render_api_error(request, message, status=400):

    content = {'message': message}
    raw_content = json.dumps(content)

    return HttpResponse(raw_content, content_type=JSON_CONTENT_TYPE, status=status)


def render_queryset_api_response(request, content):

    response = HttpResponse(content_type=JSON_CONTENT_TYPE)
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(content, stream=response, indent=2)

    return response


def api_index(request):

    urls = []

    def make_url(url_list, name):
        url_list.append({"path": reverse(name), "name": name})

    make_url(urls, "api_index")
    make_url(urls, "api_beta_code_to_unicode")
    make_url(urls, "api_works_list")

    return render_api_response(request, urls)


def api_version_info(request):

    try:
        version_info = json.loads(loader.get_template('VERSION.json').render())
    except TemplateDoesNotExist:
        version_info = {}

    return render_api_response(request, version_info)


@cache_page(8 * hours)
def api_works_stats(request):
    greek_works_count = Work.objects.filter(language="Greek").count()
    english_works_count = Work.objects.filter(language="English").count()

    stats = {
        'greek_works_count': greek_works_count,
        'english_works_count': english_works_count
    }

    return render_api_response(request, stats)


@cache_page(1 * hours)
def api_works_typeahead_hints(request):

    hints = []

    # Get the names of works
    for work in Work.objects.all().values('title', 'title_slug'):
        hints.append({
            'desc': work['title'],
            'url': reverse('read_work', args=[work['title_slug']])
        })

    #hints.extend(Work.objects.all().values_list('title', flat=True))

    # Get the author names
    for author in uniquefy(Author.objects.all().values_list('name', flat=True)):
        hints.append({
            'desc': author,
            'url': ''
        })
    #hints.extend(Author.objects.all().values_list('name', flat=True))

    # Uniquefy the list
    #hints = uniquefy(hints)

    # Return the results
    return render_api_response(request, hints)


@cache_page(15 * minutes)
def api_search_stats(request, search_text=None):

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
            include_related_forms = bool(int(request.GET['related_forms']))
        except ValueError:
            include_related_forms = False
    else:
        include_related_forms = False

    # Determine if the diacritics ought to be ignored
    if 'ignore_diacritics' in request.GET:
        try:
            ignore_diacritics = bool(int(request.GET['ignore_diacritics']))
        except ValueError:
            ignore_diacritics = False
    else:
        ignore_diacritics = False

    stats = search_stats(
        search_text, include_related_forms=include_related_forms, ignore_diacritics=ignore_diacritics)

    return render_api_response(request, stats)


@cache_page(15 * minutes)
def api_search(request, search_text=None):

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
            include_related_forms = bool(int(request.GET['related_forms']))
        except ValueError:
            include_related_forms = False
    else:
        include_related_forms = False

    # Determine if the diacritics ought to be ignored
    if 'ignore_diacritics' in request.GET:
        try:
            ignore_diacritics = bool(int(request.GET['ignore_diacritics']))
        except ValueError:
            ignore_diacritics = False
    else:
        ignore_diacritics = False

    # Perform the search
    search_results = search_verses(search_text, page=page, pagelen=pagelen,
                                   include_related_forms=include_related_forms, ignore_diacritics=ignore_diacritics)

    # This will be were the results are stored
    results_lists = []

    # Prepare the results
    for result in search_results.verses:

        d = {}

        # Build the list of arguments necessary to make the URL
        args = [result.verse.division.work.title_slug]
        args.extend(result.verse.division.get_division_indicators())

        # Determine if the last verse is a lone verse. If it is, then don't put the verse in the URL args.
        if Verse.objects.filter(division=result.verse.division).count() > 1:
            division_has_multiple_verses = True
            args.append(str(result.verse))
        else:
            division_has_multiple_verses = False

        d['url'] = reverse('read_work', args=args)
        d['verse'] = str(result.verse)
        d['division'] = result.verse.division.get_division_description()
        d['work_title_slug'] = result.verse.division.work.title_slug
        d['work'] = result.verse.division.work.title
        d['highlights'] = result.highlights
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
    stats = search_stats(
        search_text, include_related_forms=include_related_forms, ignore_diacritics=ignore_diacritics)

    results_set = {
        'result_count': search_results.result_count,
        'page': search_results.page,
        'page_len': search_results.pagelen,
        'results': results_lists,
        'matched_terms': stats['matched_terms'],
        'matched_terms_verses': search_results.matched_terms,
        'matched_terms_no_diacritics': search_results.matched_terms_no_diacritics,
        'match_count': stats['matches'],
        'matched_sections': search_results.matched_sections,
        'matched_works': stats['matched_works']
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
            if re.match("\w+", value):
                # If is just ASCII, then convert it
                new_q = new_q + Greek.beta_code_to_unicode(value)
            else:
                # Otherwise, don't. It may be Greek already
                new_q = new_q + value

        # Add the query to the list
        new_queries.append(new_q)

    return render_api_response(request, " ".join(new_queries))


@cache_page(15 * minutes)
def api_word_parse(request, word=None):

    if word is None or len(word) == 0 and 'word' in request.GET:
        word = request.GET['word']

    word_basic_form = language_tools.strip_accents(normalize_unicode(word))

    # Do a search for the parse
    ignoring_diacritics = False
    ignoring_numerals = False
    descriptions = get_word_descriptions(word, False)

    # If we couldn't find the word, then try again ignoring diacritical marks
    if len(descriptions) == 0:
        ignoring_diacritics = True
        descriptions = get_word_descriptions(word, True)

    # If we couldn't find the word and it has numbers (indicating a particular parse, then remove the numbers and try again)
    if len(descriptions) == 0 and re.search("[0-9]", word) is not None:

        # Strip the numbers
        stripped_word = normalize_unicode(re.sub("[0-9]", "", word))

        ignoring_numerals = True

        # Try without ignoring diacritics
        ignoring_diacritics = False
        descriptions = get_word_descriptions(stripped_word, False)

        # Try with ignoring diacritics
        if len(descriptions) == 0:
            ignoring_diacritics = True
            descriptions = get_word_descriptions(stripped_word, True)

    # Make the final result to be returned
    results = []

    for d in descriptions:

        entry = {}

        entry["meaning"] = d.meaning
        entry["description"] = str(d)
        entry["ignoring_numerals"] = ignoring_numerals
        entry["ignoring_diacritics"] = ignoring_diacritics
        entry["form"] = d.word_form.form

        language = None

        if d.lemma:
            entry["lemma"] = d.lemma.lexical_form
            language = d.lemma.language
        else:
            entry["lemma"] = None

        # Calculate the similarity so that sort the results by similarity
        entry["similarity"] = int(round(difflib.SequenceMatcher(
            None, entry["lemma"], word_basic_form).ratio() * 100, 0))

        # Add in the lexicon references
        lexicon_entries = []

        #lemma = LexiconEntry.objects.all()[0].lemma
        #entries = LexiconEntry.objects.filter(lemma=lemma)

        """
        for entry in LexiconEntry.objects.filter(lemma=d.lemma).values('work__id', 'work__title', 'verse__original_content', 'lemma__lexical_form'):
            lexicon_entries.append({
                'work_id': 
            })
        """

        lexicon_entries = []

        def text_transformation_fx(text, parent_node, dst_doc): return transform_perseus_text(
            text, parent_node, dst_doc, None)

        for lexicon_entry in LexiconEntry.objects.filter(lemma=d.lemma):
            lexicon_entries.append({
                'work_id': lexicon_entry.work.id,
                'work_title': lexicon_entry.work.title,
                'definition': convert_xml_to_html5(lexicon_entry.verse.original_content, return_as_str=True, text_transformation_fx=text_transformation_fx),
                'lemma_lexical_form': lexicon_entry.lemma.lexical_form
            })

        entry['lexicon_entries'] = lexicon_entries

        results.append(entry)

    # If we are ignoring diacritics, then sort the entries by the similarity
    def word_compare(x, y):
        return y["similarity"] - x["similarity"]

    results = sorted(results, key=cmp_to_key(word_compare))

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

    d['forms'] = GreekVariations.get_variations(
        word, include_beta_code=True, include_alternate_forms=True, ignore_diacritics=False, messages=messages)
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
    works = works.order_by("title").prefetch_related(
        'authors').prefetch_related('editors')

    # Make the resulting JSON
    works_json = []

    for work in works:

        works_json.append({
            'title': work.title,
            'title_slug': work.title_slug,
            'language': work.language,
            'author': ", ".join(work.authors.values_list('name', flat=True)),
            'editor': ", ".join(work.editors.values_list('name', flat=True)),
        })

    return render_api_response(request, works_json)


def api_read_work(request, author=None, language=None, title=None, division_0=None, division_1=None, division_2=None, division_3=None, division_4=None, leftovers=None, **kwargs):
    data = get_work_page_info(author, language, title, division_0, division_1,
                              division_2, division_3, division_4, leftovers, logger=logger)

    # Return a 404 if the work could not be found
    if data is None:
        return render_api_response(request, [], status=404)

    # If the verse could not be found, set a response code to note that we couldn't get the content that the user wanted so that caching doesn't take place
    status_code = 200
    if data['verse_not_found']:
        status_code = 210

    # Convert the content to JSON
    data_json = {}
    for k, v in data.items():
        if hasattr(v, '__dict__'):
            data_json[k] = v.__dict__
        else:
            data_json[k] = v

    return render_api_response(request, data, status=status_code, cache_timeout=12 * months)


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
                arg = arg.replace(slugify(d['descriptor']), d['descriptor'])

        results.append(arg)

    return results


def parse_reference_and_get_division_and_verse(regex, escaped_ref, work, divisions_with_spaces):

    # Try parsing the reference normally
    division_0, division_1, division_2, division_3, division_4 = assign_divisions(
        re.split(regex, escaped_ref))

    # Swap back the slugs
    division_0, division_1, division_2, division_3, division_4 = swap_slugs(
        divisions_with_spaces, division_0, division_1, division_2, division_3, division_4)

    # Try to resolve the division
    division, verse_to_highlight = get_division_and_verse(
        work, division_0, division_1, division_2, division_3, division_4)

    return division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4


def get_work_info(title):

    # Try to get the work
    work_alias = get_object_or_404(WorkAlias, title_slug=title)
    work = work_alias.work

    # Add the work info
    content = {
        'title': work.title,
        'authors': None,
        'editors': None,
        'language': work.language,
        'title_slug': work.title_slug
    }

    # Add the author info
    if work.authors.count() > 0:
        authors = []

        for author in work.authors.all():

            # Get the author
            authors.append(author.name)

        content['authors'] = authors

    # Add the editor info
    if work.editors.all().count() > 0:
        editors = []

        for editor in work.editors.all():

            # Get the editor
            editors.append(editor.name)

        content['editors'] = editors

    # Get the wikipedia information
    query = work.title

    query2 = None
    query3 = None

    if work.authors.all().count() > 0:
        query2 = work.title + " " + work.authors.all()[:1][0].name
        query3 = work.authors.all()[:1][0].name

    wiki_content = get_wikipedia_info_multiple(query, query2, query3)

    if wiki_content is not None:
        content['wiki_info'] = wiki_content

    # Get the WorkSource
    try:
        worksource = WorkSource.objects.get(work=work)

        content['source'] = worksource.source
        content['source_description'] = worksource.description
    except ObjectDoesNotExist:
        content['source'] = None
        content['source_description'] = None

    return content


def api_work_info(request, title):

    content = get_work_info(title)

    if content is not None:
        return render_api_response(request, content)

    # Couldn't find the work
    return render_api_response(request, {'work': title}, status=404)


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


def get_wikipedia_info_multiple(topic=None, topic2=None, topic3=None):

    topics = []

    # Get the topic from the arguments
    if topic is not None:
        topics.append(topic)

    if topic2 is not None:
        topics.append(topic2)

    if topic3 is not None:
        topics.append(topic3)

    import sys
    sys.path.append("lib")

    import wikipedia
    from wikipedia import PageError, DisambiguationError

    topic_override = None

    # See if an article is listed for this search term
    for t in topics:
        topic_override = WikiArticle.get_wiki_article(t)

        if topic_override is not None:
            break

    # Use the topic from the wiki article list if we got one
    if topic_override is not None:
        topics.insert(0, topic_override)
    else:
        logger.info("Failed to find wiki article for topics=%r",
                    ",".join(topics))

    # Get the wiki article
    for t in topics:
        content = get_wikipedia_info(t)

        if content is not None:
            return content


@cache_page(4 * hours)
def api_wikipedia_info(request, topic=None, topic2=None, topic3=None):

    # Get the topic from the arguments
    if topic is None and 'topic' in request.GET:
        topic = request.GET['topic']

    if topic2 is None and 'topic2' in request.GET:
        topic2 = request.GET['topic2']

    if topic3 is None and 'topic3' in request.GET:
        topic3 = request.GET['topic3']

    content = get_wikipedia_info_multiple(topic, topic2, topic3)

    if content is not None:
        return render_api_response(request, content)

    # Couldn't find the article
    return render_api_response(request, {'topic': topic}, status=404)


def api_resolve_reference(request, work=None, ref=None):

    # Get the work and reference from the arguments
    if work is None and 'work' in request.GET:
        work = request.GET['work']

    if ref is None and 'ref' in request.GET:
        ref = request.GET['ref']

    # Get the work that is being referred to
    work_alias = get_object_or_404(WorkAlias, title_slug=work)

    # Get the division names that have spaces in them
    divisions_with_spaces = Division.objects.filter(
        work=work_alias.work, descriptor__contains=' ').values('descriptor')

    # Start making the arguments the we need for making the URL
    args = [work_alias.work.title_slug]

    # Swap out the titles of the divisions with spaces in the name with the title slug (we will swap them back when we are done)
    escaped_ref = ref + ''

    for d in divisions_with_spaces:
        escaped_ref = escaped_ref.replace(
            d['descriptor'], slugify(d['descriptor']))

    # Try to resolve the division
    division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4 = parse_reference_and_get_division_and_verse(
        '[ .:]+', escaped_ref, work_alias.work, divisions_with_spaces)

    # If parsing it normally didn't parse right, then try without using the period as a separator
    if division is None and division_0 is not None:
        division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4 = parse_reference_and_get_division_and_verse(
            '[ :]+', escaped_ref, work_alias.work, divisions_with_spaces)

    l = [division_0, division_1, division_2, division_3, division_4]

    args.extend([x for x in l if x is not None])

    # Get the full reference of the divisions
    divisions = [x for x in l if x is not None]

    # Drop the last division ID since this is the verse if one was found
    if verse_to_highlight:
        divisions = divisions[:-1]

    # Make the response
    try:
        if division is not None:
            response_code = 200
        else:
            response_code = 404

        data = {
            'url': reverse('read_work', args=args),
            'verse_to_highlight': verse_to_highlight,
            'divisions': divisions,
            'work_title': work_alias.work.title,
            'division_title': division.get_division_description() if division else None,
        }
    except NoReverseMatch:
        response_code = 404
        data = {}

    return render_api_response(request, data, response_code)
