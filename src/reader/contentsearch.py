import whoosh
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, NUMERIC, TEXT
from whoosh.analysis import SimpleAnalyzer
from whoosh.query import Variations
from whoosh.util import rcompile
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
        
        # Add an analyzer that allows diacritical marks to be within the search queries
        analyzer = SimpleAnalyzer( rcompile(r"[\w/*()=\\+|&']+(\.?[\w/*()=\\+|&']+)*") )
        slug_analyzer = SimpleAnalyzer( rcompile(r"[a-z0-9-]+") )
        section_analyzer = SimpleAnalyzer( rcompile(r"[a-zA-Z0-9- ]+") )
        
        return Schema( verse_id      = NUMERIC(unique=True, stored=True),
                       content       = TEXT(analyzer=analyzer),
                       no_diacritics = TEXT(analyzer=analyzer),
                       work_id       = TEXT,
                       section_id    = TEXT,
                       work          = TEXT(analyzer=slug_analyzer),
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
    def index_all_works(cls):
        """
        Indexes all verses for all works.
        """
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        for work in Work.objects.all():
            cls.index_work(work)
    
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
        writer = inx.writer()
        writer.commit(optimize=True)
    
    @classmethod
    def index_work(cls, work):
        """
        Indexes all verses within the given work.
        
        Arguments:
        work -- The work that the verse is associated with
        """
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        for division in Division.objects.filter(work=work):
            cls.index_division(division)
            
        logger.info('Successfully indexed work, work="%s", duration=%i', str(work), time() - start_time )
    
    @classmethod
    def index_division(cls, division, work=None):
        """
        Indexes all verse within the provided division.
        
        Arguments:
        division -- The division to index
        work -- The work that the division is associated with
        """
        
        inx = cls.get_index()
        writer = inx.writer()
        
        for verse in Verse.objects.filter(division=division):
            cls.index_verse(verse, division=division, writer=writer, commit=False)
            
        if work is None:
            work = division.work
            
        writer.commit()
        
        if work is not None:
            logger.info('Successfully indexed division, division="%s", work="%s"', str(division), str(work) )
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
        
        descriptions.append(unicode(division.get_division_description(use_titles=False).decode("UTF-8")))
        descriptions.append(unicode(division.get_division_description(use_titles=True).decode("UTF-8")))
        
        # Now add in the parent divisions so that they can be searched without having to specifically define the entire hierarchy
        next_division = division.parent_division
        
        # Keep recursing upwards until we hit the top
        while next_division is not None:
            descriptions.append(unicode(next_division.get_division_description(use_titles=False).decode("UTF-8")))
            descriptions.append(unicode(next_division.get_division_description(use_titles=True).decode("UTF-8")))
            
            next_division = next_division.parent_division
        
        return ",".join(descriptions)
    
    @classmethod
    def unslugify(cls, txt):
        return txt.replace('_', ' ').replace('-', ' ').title()
    
    @classmethod
    def index_verse(cls, verse, work=None, division=None, commit=False, writer=None):
        """
        Indexes the provided verse.
        
        Arguments:
        verse -- The verse to index
        work -- The work that the verse is associated with
        division -- The division that the verse is associated with
        """
        
        # Get the index
        inx = cls.get_index()
        
        # Get a writer
        if writer is None:
            writer = inx.writer()
        
        if division is None and verse is not None:
            division = verse.division
            
        if work is None and division is not None:
            work = division.work
        
        # Get the author
        if work.authors.count() > 0:
            author_str = unicode(work.authors.all()[:1][0].name)
        else:
            author_str = unicode()
        
        # Prepare the content for saving
        if verse.content is not None and len(verse.content) > 0:
            content = normalize_unicode(verse.content)
        else:
            content = normalize_unicode(verse.original_content)
        
        # Strip diacritical marks
        if work is None or work.language is None or work.language != "english":
            no_diacritics = strip_accents(verse.content)
        else:
            no_diacritics = None
        
        # Add the content
        writer.add_document(content       = content,
                            no_diacritics = no_diacritics,
                            verse_id      = verse.id,
                            work_id       = work.title_slug,
                            section_id    = division.title_slug,
                            work          = unicode(work.title) + ", " + work.title_slug,
                            section       = cls.get_section_index_text(division),
                            author        = author_str
                            )
    
        # Commit it
        if commit:
            writer.commit()
    
        #logger.info('Successfully indexed verse, verse=%s, division="%s", work="%s"', str(verse), str(division), str(work) )
        logger.info('Successfully indexed verse, verse=%s, division="%s", work="%s"', str(verse), division.get_division_description(use_titles=False), str(work) )
        
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
        
    def __init__(self, results, page, pagelen ):
        
        self.page = page
        self.pagelen = pagelen
        
        self.verses = []
        
        # Create the list of search results
        for r in results:
            
            # Get the verse so that the highlighting can be done
            verse = Verse.objects.get(id=r['verse_id'])
            
            highlights = self.get_highlights( r, verse )
            
            self.verses.append( VerseSearchResult(verse, highlights ) )
        
        self.result_count = results.results.estimated_length()
        
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
        self.matched_works = {}
        
        works = Work.objects.filter(title_slug__in=temp_matched_works.keys())
        
        for work_slug, count in temp_matched_works.items():
            
            found_work = False
            
            for work in works:
                
                if work.title_slug == work_slug:
                    self.matched_works[work.title] = count
                    found_work = True
                    continue
                
            # If we didn't find the work, then add the slug after attempting to un-slugify it
            if not found_work:
                logger.critical("Unable to find work in matched terms, work_slug=%s", work_slug)
                self.matched_works[self.unslugify(work_slug)] = count
        
        self.matched_works = OrderedDict(sorted(self.matched_works.items(), key=lambda x: x[1], reverse=True))
        
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
        
    def get_variations(self, text, include_beta_code=True, include_alternate_forms=True, ignore_diacritics=False, messages=None):
        
        # Make a signature so that we can be used to find cached results for the same request
        signature = str(include_beta_code) + "." + str(include_alternate_forms) + "." + str(ignore_diacritics) + "." + text
        
        # Get the result from the cache if available
        if signature in self.cached_variations:
            #logger.debug( "Found cached variations of the search term, word=%s, variations=%r", text, len(self.cached_variations[signature]) )
            return self.cached_variations[ signature ]
        
        logger.debug( "Looking for variations of the search term in order to perform a search, word=%s", text )
        
        forms = []
        
        if include_beta_code:
            forms.append(normalize_unicode(Greek.beta_code_to_unicode(text)))
        
        if include_alternate_forms:
            
            # Convert the content from beta-code if necessary
            text = normalize_unicode(Greek.beta_code_to_unicode(text) )
            
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
        self.cached_variations[ signature ] = forms
        
        # Return the forms
        return forms
    
    def _words(self, ixreader):
        
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
            variations.extend( self.get_variations(prepared_text, self.include_beta_code, self.include_alternate_forms, ignore_diacritics) )
        
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
    
def search_stats( search_text, inx=None, limit=2000, include_related_forms=True ):
    """
    Search verses for those with the given text and provide high-level stats about the usage of 
    
    Arguments:
    search_text -- The content to search for
    inx -- The Whoosh index to use
    limit -- A limit on the the number of verses to include
    include_related_forms -- Expand the word into all of the related forms
    """ 
    
    logger.info( 'Performing a stats search, limit=%r, include_related_forms=%r, search_query="%s"', limit, include_related_forms, search_text )
    
    # Convert the search text to unicode
    search_text = unicode(search_text)
    
    # Get the index if provided
    if inx is None:
        inx = WorkIndexer.get_index()
        
    # Perform the search
    with inx.searcher() as searcher:
        
        # Make a parser to convert the incoming search string into a search
        if include_related_forms:
            parser = QueryParser("content", inx.schema, termclass=GreekVariations)
        else:
            parser = QueryParser("content", inx.schema, termclass=GreekBetaCodeVariations)
        
        # Parse the search string into an actual search
        search_query = parser.parse(search_text)
        
        logger.debug('Search query parsed, raw_query="%s"', search_query)
        
        results = searcher.search_page(search_query, 1, limit, terms=True)
        
        stats = {
                 'matches' : 0,
                 'terms' : []
                 }
        
        vsr = VerseSearchResults([], 1, 1)
        
        # Create the list of search results
        for r in results:
            
            # Get the verse so that the highlighting can be done
            verse = Verse.objects.get(id=r['verse_id'])
            
            highlights = vsr.get_highlights( r, verse )
            
            stats['matches'] += highlights.count('<b class="', )
            
            #stats['matches'].matched_terms()
        
    return stats
        
    
def search_verses( search_text, inx=None, page=1, pagelen=20, include_related_forms=True ):
    """
    Search all verses for those with the given text.
    
    Arguments:
    search_text -- The content to search for
    inx -- The Whoosh index to use
    page -- Indicates the page number to retrieve
    pagelen -- Indicates how many entries constitute a page
    include_related_forms -- Expand the word into all of the related forms
    """
    
    logger.info( 'Performing a search, page=%r, page_len=%r, include_related_forms=%r, search_query="%s"', page, pagelen, include_related_forms, search_text )
    
    # Convert the search text to unicode
    search_text = unicode(search_text)
    
    # Get the index if provided
    if inx is None:
        inx = WorkIndexer.get_index()
    
    # Perform the search
    with inx.searcher() as searcher:
        
        # Make a parser to convert the incoming search string into a search
        if include_related_forms:
            parser = QueryParser("content", inx.schema, termclass=GreekVariations)
        else:
            parser = QueryParser("content", inx.schema, termclass=GreekBetaCodeVariations)
        
        # Parse the search string into an actual search
        search_query = parser.parse(search_text)
        
        logger.debug('Search query parsed, raw_query="%s"', search_query)
        
        # Get the search result
        search_results = VerseSearchResults( searcher.search_page(search_query, page, pagelen, terms=True), page, pagelen)
            
    return search_results

"""
# Rebuild the search indexes when the work gets updated
@receiver(post_save, sender=Work)
def work_search_index_rebuild(work, **kwargs):
    indexer = WorkIndexer()
    indexer.index_work(work)
"""