import whoosh
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, NUMERIC, TEXT
from whoosh.analysis import SimpleAnalyzer, LowercaseFilter, RegexTokenizer
from whoosh.query import Variations
import re

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from time import time
import logging

from reader.models import Verse, Division, Work
from reader.language_tools.greek import Greek
from reader.language_tools import strip_accents, normalize_unicode
from reader.utils import get_all_related_forms
from reader.templatetags.shortcuts import unslugify

import os
from collections import OrderedDict # Used to order the stats from the search

# Get an instance of a logger
logger = logging.getLogger(__name__)

class WorkIndexer:
    """
    The WorkIndexer performs the operations necessary to index Work models using Whoosh.
    """
    
    @classmethod
    def get_schema(cls):
        """
        Returns a schema for searching works.
        
        This schema will be used for indexing the works and provides information about what is a valid search term.
        
        Note that changing the schema will have no affect unless you re-create the entire index. 
        """
        
        # This analyzer allows diacritical marks to be within the search queries
        greek_word_analyzer = SimpleAnalyzer(expression="[\w/*()=\\+|&']+(\.?[\w/*()=\\+|&']+)*")
        
        # This analyzer supports section names (which include spaces)
        section_analyzer = SimpleAnalyzer(expression="[a-zA-Z0-9- ]+")
        
        # This analyzer is used for the work name
        work_analyzer = RegexTokenizer(expression="[a-zA-Z0-9- ]+") | LowercaseFilter()
        
        return Schema( verse_id      = NUMERIC(unique=True, stored=True, sortable=True),
                       content       = TEXT(analyzer=greek_word_analyzer, vector=True),
                       no_diacritics = TEXT(analyzer=greek_word_analyzer, vector=True),
                       work_id       = TEXT(stored=True),
                       section_id    = TEXT,
                       work          = TEXT(analyzer=work_analyzer),
                       section       = TEXT(analyzer=section_analyzer),
                       author        = TEXT)
    
    @classmethod
    def get_index_dir(cls):
        """
        Gets the directory where indexes will be stored.
        """
        
        if settings.SEARCH_INDEXES:
            return settings.SEARCH_INDEXES
        else:
            return os.path.join("..", "var", "indexes")
    
    @classmethod
    def index_dir_exists(cls):
        """
        Determines if the index directory exists.
        """
        
        return os.path.exists( cls.get_index_dir() )
        
    @classmethod
    def get_index(cls, create=False):
        """
        Get a Whoosh index.
        
        Arguments:
        create -- If true, the index files be initialized
        """
        
        # Get a reference to the indexes path
        index_dir = cls.get_index_dir()
        
        # Make the directory if it does not exist
        if create and not os.path.exists(index_dir):
            logger.info("Creating the index directories")
            os.makedirs(index_dir)
        
        # Make the storage object with a reference to the indexes directory
        storage = FileStorage( index_dir )
        
        # Get a reference to the schema
        schema = cls.get_schema()
        
        # Create the verses index
        if create:
            inx = storage.create_index(schema)
        
        # Open the index
        else:
            inx = whoosh.index.open_dir(index_dir)
        
        # Return a reference to the index
        return inx
    
    @classmethod
    def is_work_in_index(cls, work):
        
        inx = WorkIndexer.get_index()
        
        # Perform the search
        with inx.searcher() as searcher:
            
            parser = QueryParser("work", inx.schema)
            query_str = work.title_slug
            search_query = parser.parse(query_str)
            
            results = searcher.search_page(search_query, 1, 1)
            return len(results) > 0
            
    @classmethod
    def get_writer(cls, inx=None):
        """
        Get a writer that can be used to update the search indexes.
        """
        
        if inx is None:
            inx = cls.get_index()
        
        return inx.writer(limitmb=settings.SEARCH_INDEXER_MEMORY_MB, procs=settings.SEARCH_INDEXER_PROCS)
    
    @classmethod
    def index_all_works(cls, commit_only_once=False, index_only_if_empty=True):
        """
        Indexes all verses for all works.
        """
        
        logger.info("Beginning updating the index of all available works, indexing_only_if_empty=%r", index_only_if_empty)
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        if commit_only_once:
            writer = cls.get_writer()
        else:
            writer = None
        
        for work in Work.objects.all():
            
            # If we are only indexing if the index does not contain the document, then check first
            if index_only_if_empty and cls.is_work_in_index(work):
                logger.info("Work already in index and will be skipped, work=%s", str(work.title_slug))
                
                # Skip to the next document
                continue
            
            if not commit_only_once:
                cls.index_work(work, commit=True)
            else:
                cls.index_work(work, commit=False, writer=writer)
    
        # Commit at the end to reduce the time it takes to index
        if commit_only_once and writer is not None:
            writer.commit()
        
        logger.info("Successfully indexed all works, duration=%i", time() - start_time )
    
    @classmethod
    def delete_work_index(cls, work=None, work_title_slug=None):
        """
        Deletes the index for the given work. Either the work or the work_title_slug parameter must be provided.
        
        Arguments:
        work -- The work that the index entries will be deleted of
        work_title_slug -- The slug of the work to delete the indexes of
        """
        
        if work_title_slug is None and work is None:
            return False
        
        elif work_title_slug is None and work is not None:
            work_title_slug = work.title_slug
        
        inx = cls.get_index(False)
        
        parser = QueryParser("content", inx.schema)
        inx.delete_by_query(parser.parse(u'work:' + work_title_slug))
        writer = cls.get_writer(inx)
        writer.commit(optimize=True)
    
    @classmethod
    def index_work(cls, work, commit=True, writer=None):
        """
        Indexes all verses within the given work.

        Arguments:
        work -- The work that the verse is associated with
        commit -- Indicates whether the changes should be committed to the persistence
        writer -- The index writer to write to.
        """
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        if writer is None:
            writer = cls.get_writer()
            
            commit = True
        
        for division in Division.objects.filter(work=work):
            cls.index_division(division, commit=False, writer=writer)
        
        if commit and writer is not None:
            writer.commit()
            
        logger.info('Successfully indexed work, work="%s", duration=%i', str(work.title_slug), time() - start_time )
    
    @classmethod
    def index_division(cls, division, work=None, commit=False, writer=None):
        """
        Indexes all verse within the provided division.
        
        Arguments:
        division -- The division to index
        work -- The work that the division is associated with
        """
        
        if writer is None:
            writer = cls.get_writer()
            
            commit = True
        
        for verse in Verse.objects.filter(division=division):
            cls.index_verse(verse, division=division, writer=writer, commit=False)
            
        if work is None:
            work = division.work
            
        if commit and writer is not None:
            writer.commit()
        
        if work is not None:
            logger.info('Successfully indexed division, division="%s", work="%s"', str(division), str(work.title_slug) )
        else:
            logger.info('Successfully indexed division, division="%s"', str(division) )
    
    @classmethod
    def get_section_index_text(cls, division):
        """
        Creates a string list of the ways in which the given division can be referenced.
        
        Arguments:
        division -- The division to create the section description of
        """
        descriptions = []
        
        descriptions.append(division.get_division_description(use_titles=False))
        descriptions.append(division.get_division_description(use_titles=True))
        
        # Now add in the parent divisions so that they can be searched without having to specifically define the entire hierarchy
        next_division = division.parent_division
        
        # Keep recursing upwards until we hit the top
        while next_division is not None:
            descriptions.append(next_division.get_division_description(use_titles=False))
            descriptions.append(next_division.get_division_description(use_titles=True))
            
            next_division = next_division.parent_division

        return ",".join(descriptions)
    
    @classmethod
    def replace_empty_string(cls, val):
        """
        This function will replace empty strings with a non-empty string. This is necessary to workaround a bug in Whoosh that causes corruption of the index.
        
        https://bitbucket.org/mchaput/whoosh/issues/439/block-tag-error-vpst-generated-on-indexing
        
        Arguments:
        val -- A string which may be empty
        """
    
        if val is None or len(val.strip()) == 0:
            return u"()"
        else:
            return val
    
    @classmethod
    def index_verse(cls, verse, work=None, division=None, commit=False, writer=None):
        """
        Indexes the provided verse.
        
        Arguments:
        verse -- The verse to index
        work -- The work that the verse is associated with
        division -- The division that the verse is associated with
        """
        
        # Get a writer
        if writer is None:
            writer = cls.get_writer()
        
        if division is None and verse is not None:
            division = verse.division
            
        if work is None and division is not None:
            work = division.work
        
        # Get the author
        if work.authors.count() > 0:
            author_str = work.authors.all()[:1][0].name
        else:
            author_str = ''
        
        # Prepare the content for saving
        if verse.content is not None and len(verse.content) > 0:
            content = normalize_unicode(verse.content)
        else:
            logger.debug('Found empty content for verse=%s, division="%s", work="%s"', str(verse), division.get_division_description(use_titles=False), str(work.title_slug) )
            content = None#normalize_unicode(verse.original_content)
        
        # Strip diacritical marks
        if work is None or work.language is None or work.language != "english":
            no_diacritics = strip_accents(verse.content)
        else:
            no_diacritics = None
        
        if content is not None:
            # Add the content
            writer.add_document(content       = cls.replace_empty_string(content),
                                no_diacritics = cls.replace_empty_string(no_diacritics),
                                verse_id      = verse.id,
                                work_id       = work.title_slug,
                                section_id    = division.title_slug,
                                work          = work.title + "," + work.title_slug,
                                section       = cls.get_section_index_text(division),
                                author        = author_str
                                )
    
        # Commit it
        if commit:
            writer.commit()
    
        #logger.info('Successfully indexed verse, verse=%s, division="%s", work="%s"', str(verse), str(division), str(work.title_slug) )
        logger.info('Successfully indexed verse, verse=%s, division="%s", work="%s"', str(verse), division.get_division_description(use_titles=False), str(work.title_slug) )
        
class VerseSearchResults:
    
    def add_to_results_string(self, to_str, from_str, separator="..."):
        
        if to_str is None:
            to_str = ''
            
        if from_str is not None:
            
            if to_str is not None and len(to_str) > 0:
                to_str = to_str + separator + from_str
            else:
                to_str = from_str
                
        return to_str
    
    def get_highlights(self, result, verse):
        
        highlights_str = ''
        
        highlights_str = self.add_to_results_string(highlights_str, result.highlights("content", text=normalize_unicode(verse.content)))
        
        highlights_str = self.add_to_results_string(highlights_str, result.highlights("no_diacritics", text=strip_accents(verse.content)) )        
    
        return highlights_str
        
    def __init__(self, results, page, pagelen, use_estimated_length=False ):
        
        self.page = page
        self.pagelen = pagelen
        
        self.verses = []
        
        # Create the list of search results
        for r in results:
            
            # Get the verse so that the highlighting can be done
            verse = Verse.objects.get(id=r['verse_id'])
            
            highlights = self.get_highlights( r, verse )
            
            self.verses.append( VerseSearchResult(verse, highlights ) )
        
        if use_estimated_length:
            self.result_count = results.results.estimated_length()
        else:
            self.result_count = len(results.results)
        
        temp_matched_terms = {}
        temp_matched_terms_no_diacritics = {}
        
        temp_matched_works = {}
        temp_matched_sections = {}
        
        self.match_count = 0
        
        # Add the matched terms if available
        if results.results.has_matched_terms():
            for term, term_matches in results.results.termdocs.items():
                
                # Include terms matched 
                if term[0] == "content":
                    temp_matched_terms[term[1]] = len(term_matches)
                    self.match_count += len(term_matches)
                    
                # Include terms matched that matched without diacritics
                if term[0] == "no_diacritics":
                    temp_matched_terms_no_diacritics[term[1]] = len(term_matches)
                    
                # Include section matches
                if term[0] == "section":
                    temp_matched_sections[term[1]] = len(term_matches)
                    
                # Include work matches
                if term[0] == "work":
                    temp_matched_works[term[1]] = len(term_matches)
                    
        # Sort the dictionaries
        self.matched_terms = OrderedDict(sorted(temp_matched_terms.items(), key=lambda x: x[1], reverse=True))
        self.matched_terms_no_diacritics = OrderedDict(sorted(temp_matched_terms.items(), key=lambda x: x[1], reverse=True))
        self.matched_sections = OrderedDict(sorted(temp_matched_sections.items(), key=lambda x: x[1], reverse=True))
        #self.matched_works = OrderedDict(sorted(temp_matched_works.items(), key=lambda x: x[1], reverse=True)) 
        
        # De-reference the name of the works
        self.matched_works = replace_work_names_with_titles(temp_matched_works)
        
class VerseSearchResult:
    
    def __init__(self, verse, highlights):
        self.verse = verse
        self.highlights = highlights
    
class GreekVariations(Variations):
    """
    Provides variations of a Greek word including a beta-code representation and all related forms. This way, users can search
    using beta-code if they don't have a Greek keyboard enabled. Additionally, then can get 
    """
    
    variation_fields = ['no_diacritics', 'content']
    
    def __init__(self, fieldname, text, boost=1.0, include_beta_code=True, include_alternate_forms=True):
        super(GreekVariations,self).__init__( fieldname, text, boost )
        
        self.include_beta_code       = include_beta_code
        self.include_alternate_forms = include_alternate_forms
        
        # This cache helps improve performance by reducing unnecessary database queries for variations that we have already looked up.
        # This was added because it was found that Whoosh makes multiple requests for the same variation repeatedly.
        self.cached_variations = {}
        
    @classmethod
    def get_variations(cls, text, include_beta_code=True, include_alternate_forms=True, ignore_diacritics=False, messages=None, cached_variations=None):
        
        # Make a signature so that we can be used to find cached results for the same request
        signature = str(include_beta_code) + "." + str(include_alternate_forms) + "." + str(ignore_diacritics) + "." + text
        
        # Get the result from the cache if available
        if cached_variations is not None and signature in cached_variations:
            #logger.debug( "Found cached variations of the search term, word=%s, variations=%r", text, len(cached_variations[signature]) )
            return cached_variations[ signature ]
        
        logger.debug( "Looking for variations of the search term in order to perform a search, word=%s", text )
        
        forms = []
        
        if include_beta_code:
            forms.append(normalize_unicode(Greek.beta_code_to_unicode(text)))
        
        if include_alternate_forms:
            
            # Convert the content from beta-code if necessary
            text = normalize_unicode(Greek.beta_code_to_unicode(text))
            
            # Get the related forms
            related_forms = get_all_related_forms(text, ignore_diacritics)
            
            # If we couldn't find any related forms, then try finding them without diacritical marks
            if len(related_forms) == 0 and ignore_diacritics == False:
                related_forms = get_all_related_forms(text, True)
                
                if len(related_forms) > 0:
                    logger.debug( "Variations could be only found by ignoring diacritical marks, word=%s", text )
                
                # Make a message noting that we couldn't find any variations of the word
                if len(related_forms) > 0 and messages is not None:
                    messages.append("Variations of %s could be only found by ignoring diacritical marks" % text)
            
            # Make a message noting that we couldn't find any variations of the word
            if len(related_forms) == 0 and messages is not None:
                messages.append("No variations of %s could be found" % text)
                
            elif len(related_forms) == 0:
                logger.debug( "No variations could be found, word=%s", text )
                
            # Make a message noting that variations were found
            if len(related_forms) > 0 and messages is not None:
                messages.append("Found variations of the search term, word=%s, variations=%r" % (text, len(related_forms)))
            
            elif len(related_forms) > 0:
                logger.debug("Found variations of the search term, word=%s, variations=%r", text, len(related_forms))
            
            # Add the related forms
            for r in related_forms:
                if ignore_diacritics:
                    forms.append(strip_accents(r.form))
                else:
                    forms.append(r.form)
        
        # Cache the result
        if cached_variations is not None:
            cached_variations[ signature ] = forms
        
        # Return the forms
        return forms
    
    def _btexts(self, ixreader):
        
        # Determine if we are searching the field that is stripped of diacritical marks
        if self.fieldname == "no_diacritics":
            ignore_diacritics = True
            
            # Strip diacritical beta-code characters in case the user wants to search for words regardless of diacritical
            # marks but includes them in the search term
            prepared_text = re.sub(r'[\/()*=&+|]', '', self.text) 
        else:
            ignore_diacritics = False
            prepared_text = self.text
        
        # This will be the array of variations
        variations = []
        
        # If the field doesn't contain diacritics then make sure to strip them from the word
        if ignore_diacritics:
            prepared_text = strip_accents(prepared_text)
            
        # Add the text we are searching for as a variation
        variations.append( prepared_text )
        
        # Add the other Greek variations
        if GreekVariations.variation_fields is None or self.fieldname in GreekVariations.variation_fields:
            variations.extend( GreekVariations.get_variations(prepared_text, self.include_beta_code, self.include_alternate_forms, ignore_diacritics, None, self.cached_variations) )
        
        # Return the variations list
        return [word for word in variations
                if (self.fieldname, word) in ixreader]
        
class GreekBetaCodeVariations(GreekVariations):
    """
    Provides variations of a Greek word including a beta-code representation. This way, users can search
    using beta-code if they don't have a Greek keyboard enabled.
    
    Note that other forms related to the same lemma will not be included.
    """
    
    def __init__(self, fieldname, text, boost=1.0):
        super(GreekBetaCodeVariations,self).__init__( fieldname, text, boost, True, False )
    
def replace_work_names_with_titles(list_of_matches_in_works):
    works = Work.objects.filter(title_slug__in=list_of_matches_in_works.keys())
    matched_works = {}
    
    for work_slug, count in list_of_matches_in_works.items():
        
        found_work = False
        
        for work in works:
            if work.title_slug == work_slug:
                matched_works[work.title] = count
                found_work = True
                continue
            
        # If we didn't find the work, then add the slug after attempting to un-slugify it
        if not found_work:
            logger.critical("Unable to find work in matched terms, work_slug=%s", work_slug)
            matched_works[unslugify(work_slug)] = count
    
    matched_works = OrderedDict(sorted(matched_works.items(), key=lambda x: x[1], reverse=True))
    
    return matched_works
    
    
def search_stats( search_text, inx=None, limit=2000, include_related_forms=True, ignore_diacritics=False ):
    """
    Search verses for those with the given text and provide high-level stats about the usage of this term. This function is necessary because Whoosh
    term matching stats indicate the number of verses that contain the given term, not the count of absolute count of the term.
    
    Arguments:
    search_text -- The content to search for
    inx -- The Whoosh index to use
    limit -- A limit on the the number of verses to include
    include_related_forms -- Expand the word into all of the related forms
    ignore_diacritics -- Search ignoring dia-critical marks by default
    """ 
    
    logger.info( 'Performing a stats search, limit=%r, include_related_forms=%r, search_query="%s"', limit, include_related_forms, search_text )

    # Get the index if provided
    if inx is None:
        inx = WorkIndexer.get_index()
        
    # Perform the search
    with inx.searcher() as searcher:
        
        # Determine which field will be searched by default
        default_search_field = "content"
        
        if ignore_diacritics:
            default_search_field = "no_diacritics"
        
        # Make a parser to convert the incoming search string into a search
        if include_related_forms:
            parser = QueryParser(default_search_field, inx.schema, termclass=GreekVariations)
        else:
            parser = QueryParser(default_search_field, inx.schema, termclass=GreekBetaCodeVariations)
        
        # Parse the search string into an actual search
        search_query = parser.parse(search_text)
        
        logger.debug('Search query parsed, default_search_field="%s", raw_query="%s"', default_search_field, search_query)
        
        results = searcher.search_page(search_query, 1, limit, terms=True, sortedby="verse_id")
        
        stats = {
                 'matches' : 0
                 }
        
        # Build a list of the matched terms
        matched_terms = {}
        
        if results.results.has_matched_terms():
            for term, term_matches in results.results.termdocs.items():
                if term[0] == "content":
                    matched_terms[term[1].decode('utf-8')] = 0
                    
                if term[0] == "no_diacritics":
                    matched_terms[term[1].decode('utf-8')] = 0
        
        results_count = 0
                      
        # Build a list of matched works
        matched_works = {}
        
        # Iterate through the search results
        for r in results:
            
            results_count += 1
            matched_in_result = 0
            
            # For each document: get the matched terms
            docnum = searcher.document_number(verse_id=r['verse_id'])
            
            # Process the main content
            for term in searcher.vector(docnum,"content").items_as("frequency"):
                
                for matched_term in matched_terms:
                    
                    if matched_term == normalize_unicode(term[0]):
                        matched_terms[matched_term] += term[1]
                        matched_in_result += term[1]
                        
            # Process the no_diacritics content
            for term in searcher.vector(docnum,"no_diacritics").items_as("frequency"):
                
                for matched_term in matched_terms:
                    
                    if matched_term == normalize_unicode(term[0]):
                        matched_terms[matched_term] += term[1]
                        matched_in_result += term[1]
            
            stats['matches'] += matched_in_result
            
            # Get the stored fields so that we determine which works were matched 
            fields = searcher.stored_fields(docnum)
            
            for field, value in fields.items():
                
                # Make sure that this field is for the work
                if field == "work_id":
                    
                    # Add the number of matches
                    if value in matched_works:
                        matched_works[value] = matched_works[value] + matched_in_result
                    else:
                        matched_works[value] = matched_in_result
        
        stats['matched_works'] = replace_work_names_with_titles(matched_works)
        
        stats['matched_terms'] = OrderedDict(sorted(matched_terms.items(), key=lambda x: x[1], reverse=True))
        stats['results_count'] = results_count
    
    return stats

def search_verses( search_text, inx=None, page=1, pagelen=20, include_related_forms=True, ignore_diacritics=False ):
    """
    Search all verses for those with the given text.
    
    Arguments:
    search_text -- The content to search for
    inx -- The Whoosh index to use
    page -- Indicates the page number to retrieve
    pagelen -- Indicates how many entries constitute a page
    include_related_forms -- Expand the word into all of the related forms
    ignore_diacritics -- Search ignoring dia-critical marks by default
    """
    
    logger.info( 'Performing a search, page=%r, page_len=%r, include_related_forms=%r, search_query="%s"', page, pagelen, include_related_forms, search_text )
    
    # Get the index if provided
    if inx is None:
        inx = WorkIndexer.get_index()
    
    # Perform the search
    with inx.searcher() as searcher:
        
        # Determine which field will be searched by default
        default_search_field = "content"
        
        if ignore_diacritics:
            default_search_field = "no_diacritics"
        
        # Make a parser to convert the incoming search string into a search
        if include_related_forms:
            parser = QueryParser(default_search_field, inx.schema, termclass=GreekVariations)
        else:
            parser = QueryParser(default_search_field, inx.schema, termclass=GreekBetaCodeVariations)
        
        # Parse the search string into an actual search
        search_query = parser.parse(search_text)
        
        logger.debug('Search query parsed, default_search_field="%s", raw_query="%s"', default_search_field, search_query)
        
        # Get the search result
        search_results = VerseSearchResults( searcher.search_page(search_query, page, pagelen, terms=True, sortedby="verse_id"), page, pagelen)
            
    return search_results

"""
# Rebuild the search indexes when the work gets updated
@receiver(post_save, sender=Work)
def work_search_index_rebuild(work, **kwargs):
    indexer = WorkIndexer()
    indexer.index_work(work)
"""