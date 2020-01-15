import logging
from reader.importer import TextImporter
from reader.models import Work, WorkSource
from reader import language_tools
from reader.importer.batch_import import ImportTransforms
import os
import re
from copy import copy

# Get an instance of a logger
logger = logging.getLogger(__name__)

class UnboundBibleTextImporter(TextImporter):
    """
    This importer allows texts from Biola's Unbound Bible project (http://unbound.biola.edu/).
    """
    
    def __init__(self, work=None, work_source=None, book_names_file=None, import_policy=None):
        
        self.book_names_file = book_names_file
        self.book_names = None
        
        self.division = None
        
        self.current_chapter = None
        self.current_book_index = None
        
        self.current_book_division = None
        self.current_chapter_division = None
        self.current_division = None
        
        self.current_verse = None
        self.verses_created = 0
        
        self.import_policy = import_policy
        
        TextImporter.__init__(self, work, work_source)
    
    def import_line(self, line):
        """
        Import a line from an unbound Bible file.
        
        Arguments:
        line -- The line to import
        """
        
        orig_book_index, orig_chapter, orig_verse, orig_subverse, order_by, text = line.split("\t")
        
        # If this is for a different book, then make a new division
        if orig_book_index != self.current_book_index:
            self.current_book_division = self.make_division( self.book_names[orig_book_index], self.current_division, save=False)
            self.current_book_division.title = self.book_names[orig_book_index]
            self.current_book_division.level = 1
            self.current_book_division.type = "Book"
            self.current_book_division.save()
            
            self.current_chapter_division = None
            self.current_chapter = None
            self.current_division = self.current_book_division
            
            self.current_book_index = orig_book_index
            
        # If this is for a different chapter, then make a new division
        if orig_chapter != self.current_chapter:
            self.current_chapter_division = self.make_division( orig_chapter, self.current_division, save=False)
            self.current_chapter_division.level = 2
            self.current_chapter_division.type = "Chapter"
            self.current_chapter_division.parent_division = self.current_book_division
            self.current_chapter_division.save()
            
            self.current_chapter = orig_chapter
            self.current_division = self.current_chapter_division
        
        # Make the verse
        verse = self.make_verse(self.current_verse, self.current_chapter_division, save=False)
        verse.indicator = orig_verse + orig_subverse
        verse.content = language_tools.normalize_unicode(text.strip())
        verse.save()
        
        self.verses_created = self.verses_created + 1
        logger.info('Successfully imported verse of work, verse_count=%i, title="%s"', self.verses_created, self.work.title) 
    
    def get_name_from_comment(self, line):
        """
        Get the name of the document from the comment line.
        
        Arguments:
        line -- 
        """
        
        regex = re.compile("[^\[]+")
        n, value = line.split("\t")
        
        name = regex.findall(value)[0].strip()
        
        return name
    
    def find_and_load_book_names(self, import_file_name=None):
        """
        Load the book names file. Try loading the book names from the file specified in the constructor.
        Otherwise, try loading it from the same directory where the file to import is located (if supplied).
        
        Arguments:
        import_file_name -- The path to the file to be imported
        """
        
        # Try to load the book names from the file supplied in the constructor (if supplied)
        if self.book_names_file is not None:
            book_names = self.load_book_names( self.book_names_file )
            logger.info('Loaded book names, file="%s"', self.book_names_file)
            return book_names
            
        # Try to import the book names file if it is the same directory as the 
        if import_file_name is not None:
            
            book_name_file = os.path.join( os.path.split(import_file_name)[0], "book_names.txt" )
            
            if os.path.exists( book_name_file ):
                book_names = self.load_book_names( book_name_file )
                logger.info('Loaded book names, file="%s"', book_name_file)
                return book_names
            else:
                raise Exception("Book names not found; the book_names.txt file is necessary for the import of this work to be successful")
        
    def get_processing_parameters(self, file_path, title ):
        """
        Get the processing parameters associated with the given work.
        """
        
        logger.debug("Analyzing %s to determine if it ought to be imported" % (title ) )
        
        return self.import_policy( title=title, file_path=file_path )
    
    def load_book_names(self, file_name):
        """
        Load the book names from the file path provided. The book names will be stored in the book_names
        variable of the class if successfully and they will be returned by this function.
        
        Arguments:
        file_name -- The full path to the book names file
        """
        
        # This is the temporary list of book names
        d = {}
        
        with open(file_name, 'r') as f:
            
            for line in f:
                identifier, book_name = line.split("\t")
                d[identifier] = book_name.strip()
            
        # Save the book names
        self.book_names = d
        
        return self.book_names
    
    def import_file(self, file_name):
        
        title = None
        
        if self.work is None:
            self.work = Work()
            self.work.save()
            work_created = True
            
            # Make the work source
            if self.work_source is None:
                self.work_source = WorkSource()
            
            # Save the source of the document
            self.work_source.source = "unbound.biola.edu"
            self.work_source.resource = os.path.basename(file_name)
            self.work_source.work = self.work
            self.work_source.description = "Text provided by The Unbound Bible from Biola University. Original version available for viewing and download at http://www.unboundbible.org/."
            self.work_source.save()
                
        else:
            work_created = False
        
        # Load the list of book names
        if self.book_names is None:
            self.find_and_load_book_names(file_name)
        
        # This tracks the number of lines imported
        self.verses_created = 0
        
        with open(file_name, 'r') as f:
            
            for line in f:
                
                # If the line is comment with the document name
                if line.startswith("#name"):
                    title = self.get_name_from_comment(line)
                    logger.info('Parsed name from the file, name="%s"', title)
                    
                    if work_created:
                        self.work.title = title
                        self.work.save()
                    
                # If the line starts with a pound symbol, then ignore it since it is a comment
                elif line.startswith("#"):
                    pass # Skip this line
                
                # Otherwise, import it
                else:
                    self.import_line(line)
        
        if self.import_policy is not None:
            
            # Get the import parameters
            import_parameters = self.get_processing_parameters( os.path.basename(file_name), title)
            
            # Get the transforms to be executed
            if import_parameters not in [None, True, False] and 'transforms' in import_parameters:
                transforms = import_parameters.get('transforms', None)
                
                # Create a copy since we are going to delete items from this one
                import_parameters = copy(import_parameters)
                
                # Delete the transforms because the importer constructor doesn't take this argument
                del import_parameters['transforms']
            else:
                transforms = None
            
            # Run the transforms
            if transforms is not None:
                logger.debug("Running transforms")
                ImportTransforms.run_transforms(self.work, transforms)
            else:
                logger.debug("No transforms found")
        
        logger.info('Successfully imported work title="%s", work.id=%i', self.work.title_slug, self.work.id)
        return True
    