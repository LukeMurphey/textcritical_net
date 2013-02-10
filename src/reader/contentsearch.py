import whoosh
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, NUMERIC, TEXT
from whoosh.query import *
from reader.language_tools import strip_accents

from time import time
import logging
from reader.models import Verse, Division, Work

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
        
        return Schema( verse_id      = NUMERIC(unique=True, stored=True),
                       content       = TEXT,
                       no_diacritics = TEXT,
                       work_id       = TEXT,
                       section_id    = TEXT,
                       work          = TEXT,
                       section       = TEXT,
                       author        = TEXT)
        """
        return Schema( verse_id     = NUMERIC(unique=True, stored=True),
                       content      = TEXT,
                       work_id      = NUMERIC,
                       division_id  = NUMERIC)
        """
                       
    
    @classmethod
    def get_index_dir(cls):
        """
        Gets the directory where indexes will be stored.
        """
        
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
        
        """
        # Determine the division ID
        division_id = None
        
        if division is not None:
            division_id = division.id
        elif verse.division is not None:
            division_id = verse.division.id
        
        # Determine the work ID
        work_id = None
        
        if work is not None:
            work_id = work.id
        elif division is not None and division.work is not None:
            work_id = division.work.id
        elif verse.division is not None and verse.division.work is not None:
            work_id = verse.division.work.id
        """
        
        # Get the author
        if work.authors.count() > 0:
            author_str = unicode(work.authors.all()[:1][0].name)
        else:
            author_str = unicode()
        
        # Add the content
        writer.add_document(content       = verse.content,
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
    
    def __init__(self, results, page, pagelen ):
        
        self.page = page
        self.pagelen = pagelen
        
        self.verses = []
        
        # Create the list of search results
        for r in results:
            
            # Get the verse so that the highlighting can be done
            verse = Verse.objects.get(id=r['verse_id'])
            
            self.verses.append( VerseSearchResult(verse, r.highlights("content", text=verse.content) ) )
        
        self.result_count = len(results)
        
    
class VerseSearchResult:
    
    def __init__(self, verse, highlights):
        self.verse = verse
        self.highlights = highlights
    
def search_verses( search_text, inx=None, page=1, pagelen=20 ):
    """
    Search all verses for those with the given text.
    
    Arguments:
    search_text -- The content to search for
    inx -- The Whoosh index to use
    """
    
    # Convert the search text to unicode
    search_text = unicode(search_text)
    
    if inx is None:
        inx = WorkIndexer.get_index()
    
    with inx.searcher() as searcher:
        
        """
        if work_id is not None:
            search_query = And([Term("content", search_text), Term("work_id", work_id)])
        elif author_id is not None:
            search_query = And([Term("content", search_text), Term("author_id", author_id)])
        else:
            search_query = Term("content", search_text)
        """
        
        # Make a parser to convert the incoming search string into a search
        parser = QueryParser("content", inx.schema)
        
        # Parse the search string into an actual search
        search_query = parser.parse(search_text)
        
        #query =  QueryParser("content", inx.schema).parse(search_text)
        #search_query = Term("content", search_text)
        search_results = VerseSearchResults( searcher.search_page(search_query, page, pagelen), page, pagelen)
            
    return search_results
