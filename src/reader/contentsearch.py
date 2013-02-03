import whoosh
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, NUMERIC, TEXT

from reader.models import Verse, Division, Work

import os

class WorkIndexer:
    """
    The WorkIndexer performs the operations necessary to index Work models using Whoosh.
    """
    
    def get_schema(self):
        """
        Returns a schema for searching works.
        """
        
        return Schema( verse_id     = NUMERIC(unique=True, stored=True),
                       content      = TEXT,
                       work_id      = NUMERIC,
                       division_id  = NUMERIC)
    
    def get_index_dir(self):
        """
        Gets the directory where indexes will be stored.
        """
        
        return os.path.join("..", "var", "indexes")
    
    def get_index(self, create=False):
        """
        Get a Whoosh index.
        
        Arguments:
        create -- If true, the index files be initialized
        """
        
        # Get a reference to the indexes path
        index_dir = self.get_index_dir()
        
        # Make the directory if it does not exist
        if create and not os.path.exists(index_dir):
            os.makedirs(index_dir)
        
        # Make the storage object with a reference to the indexes directory
        storage = FileStorage( index_dir )
        
        # Get a reference to the schema
        schema = self.get_schema()
        
        # Create the verses index
        if create:
            inx = storage.create_index(schema)
        
        # Open the index
        else:
            inx = whoosh.index.open_dir(index_dir) #storage.open_index(indexname=schema)
        
        # Return a reference to the index
        return inx
    
    def index_all_works(self):
        """
        Indexes all verses for all works.
        """
        
        for work in Work.objects.all():
            self.index_work(work)
    
    def index_work(self, work):
        """
        Indexes all verses within the given work.
        
        Arguments:
        work -- The work that the verse is associated with
        """
        
        for division in Division.objects.filter(work=work):
            self.index_division(division)
    
    def index_division(self, division):
        """
        Indexes all verse within the provided division.
        
        Arguments:
        division -- The division that the verse is associated with
        """
        
        for verse in Verse.objects.filter(division=division):
            self.index_verse(verse, division=division)
    
    def index_verse(self, verse, work=None, division=None):
        """
        Indexes the provided verse.
        
        Arguments:
        verse -- The verse to index
        work -- The work that the verse is associated with
        division -- The division that the verse is associated with
        """
        
        # Get the index
        inx = self.get_index()
        
        # Get a writer
        writer = inx.writer()
        
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
        
        # Add th content
        writer.add_document(content     = verse.content,
                            verse_id    = verse.id,
                            work_id     = work_id,
                            division_id = division_id
                            )
    
        # Commit it
        writer.commit()
    

    
def search_verses( search_text, inx=None ):
    """
    Search all verses for those with the given text.
    
    Arguments:
    search_text -- The content to search for
    inx -- The Whoosh index to use
    """
    
    # Convert the search text to unicode
    search_text = unicode(search_text)
    
    if inx is None:
        inx = WorkIndexer().get_index()
    
    with inx.searcher() as searcher:
        query = QueryParser("content", inx.schema).parse(search_text)
        return searcher.search(query)

