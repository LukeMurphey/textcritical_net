import whoosh
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, NUMERIC, TEXT
from whoosh.analysis import CharsetFilter, StemmingAnalyzer, SpaceSeparatedTokenizer, SimpleAnalyzer
from whoosh.support.charset import accent_map
from whoosh.query import *
from whoosh.analysis import Filter
from whoosh.util import rcompile

from django.conf import settings

from time import time
import logging

from reader.models import Verse, Division, Work
from reader.language_tools.greek import Greek
from reader.language_tools import strip_accents, normalize_unicode
from reader.utils import get_all_related_forms

import os

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
        """
        
        # Add an accent-folding filter to a stemming analyzer so that we can search irrespective to accents
        analyzer = SimpleAnalyzer( rcompile(r"[\w/*()=\+|&']+(\.?[\w/*()=\+|&']+)*") )
        
        return Schema( verse_id      = NUMERIC(unique=True, stored=True),
                       content       = TEXT(analyzer=analyzer),
                       no_diacritics = TEXT,
                       work_id       = TEXT,
                       section_id    = TEXT,
                       work          = TEXT,
                       section       = TEXT,
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
            
        logger.info("Successfully indexed work, work=%s, duration=%i", str(work), time() - start_time )
    
    @classmethod
    def index_division(cls, division):
        """
        Indexes all verse within the provided division.
        
        Arguments:
        division -- The division that the verse is associated with
        """
        
        inx = cls.get_index()
        writer = inx.writer()
        
        for verse in Verse.objects.filter(division=division):
            cls.index_verse(verse, division=division, writer=writer, commit=False)
            
        writer.commit()
        logger.info("Successfully indexed division, division=%s", str(division) )
    
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
        
        # Add the content
        writer.add_document(content       = normalize_unicode(verse.content),
                            no_diacritics = strip_accents(verse.content),
                            verse_id      = verse.id,
                            work_id       = work.title_slug,
                            section_id    = division.title_slug,
                            work          = unicode(work.title) + ", " + work.title_slug,
                            section       = unicode(division.get_division_description(use_titles=False).decode("UTF-8")) + ", " + unicode(division.get_division_description(use_titles=True).decode("UTF-8")),
                            author        = author_str
                            )
    
        # Commit it
        if commit:
            writer.commit()
    
        logger.info("Successfully indexed verse, verse=%s", str(verse))
    
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
        
        self.result_count = len(results)
        
    
class VerseSearchResult:
    
    def __init__(self, verse, highlights):
        self.verse = verse
        self.highlights = highlights
    
def greek_variations(text, include_beta_code=True, include_alternate_forms=True):
    
    forms = [text]
    
    if include_beta_code:
        forms.append(normalize_unicode(Greek.beta_code_to_unicode(text)))
                     
    if include_alternate_forms:
        
        # Get the related forms
        related_forms = get_all_related_forms(text)
        
        for r in related_forms:
            forms.append(r.form)
    
    return forms #[text, normalize_unicode(Greek.beta_code_to_unicode(text))]
    
class GreekVariations(Variations):
    """
    Provides variations of a Greek word including a beta-code representation and all related forms. This way, users can search
    using beta-code if they don't have a Greek keyboard enabled. Additionally, then can get 
    """
    
    def __init__(self, fieldname, text, boost=1.0, include_beta_code=True, include_alternate_forms=True):
        super(GreekVariations,self).__init__( fieldname, text, boost )
        
        self.include_beta_code       = include_beta_code
        self.include_alternate_forms = include_alternate_forms
    
    def _words(self, ixreader):
        fieldname = self.fieldname
        
        return [word for word in greek_variations(self.text, self.include_beta_code, self.include_alternate_forms)
                if (fieldname, word) in ixreader]
        
class GreekBetaCodeVariations(GreekVariations):
    """
    Provides variations of a Greek word including a beta-code representation. This way, users can search
    using beta-code if they don't have a Greek keyboard enabled.
    
    Note that other forms related to the same lemma will not be included.
    """
    
    def __init__(self, fieldname, text, boost=1.0):
        super(GreekBetaCodeVariations,self).__init__( fieldname, text, boost, True, False )
    
    
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
        
        # Get the search result
        search_results = VerseSearchResults( searcher.search_page(search_query, page, pagelen), page, pagelen)
            
    return search_results
