import whoosh
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, NUMERIC, TEXT

import os

class WorkIndexer:
    
    def get_schema(self):
        return Schema( verse_id     = NUMERIC(unique=True, stored=True),
                       content      = TEXT,
                       work_id      = NUMERIC,
                       division_id  = NUMERIC)
    
    def get_index_dir(self):
        return os.path.join("..", "var", "indexes")
    
    def get_index(self, create=False):
        
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
        pass
    
    def index_work(self, work):
        pass
    
    def index_division(self, division):
        pass
    
    def index_verse(self, verse, work=None, division=None):
        
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
    
    # Convert the search text to unicode
    search_text = unicode(search_text)
    
    if inx is None:
        inx = WorkIndexer().get_index()
    
    with inx.searcher() as searcher:
        query = QueryParser("content", inx.schema).parse(search_text)
        return searcher.search(query)

