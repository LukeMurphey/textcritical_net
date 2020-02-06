import logging
import re
import os
from time import time

from reader import language_tools
from reader.importer import TextImporter, LineNumber, LineNumberRange
from reader.models import Division, Work, WorkSource
from reader.shortcuts import transform_text

from django.db import transaction
from django.template.defaultfilters import slugify
import codecs

# Get an instance of a logger
logger = logging.getLogger(__name__)

class BereanBibleImporter(TextImporter):
    
    def __init__(self, work=None, work_source=None, book_names_file=None, import_policy=None):
        
        self.book_names_file = book_names_file
        self.book_names = None
        
        self.current_book_division = None
        self.current_chapter_division = None
        self.current_verse = None
        self.verses_created = 0
        self.work = None
        self.work_source = None
        
        self.import_policy = import_policy
        
        TextImporter.__init__(self, work, work_source)

    @transaction.atomic
    def import_file(self, file_name, return_created_objects=False, start_line_number=None, **kwargs):
        
        logger.debug("Importing file, file=\"%s\"", file_name )
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        # If we are returning the objects, then initialize an array to store them. Otherwise, intialize the count.
        if return_created_objects:
            objects = []
        else:
            objects = 0

        # Create the work
        if self.work is None:
            self.work = Work()
            self.work.title = "Berean Bible"
            self.work.title_slug, slug_was_already_taken = self.get_title_slug(self.work.title)
            self.work.save()

            if slug_was_already_taken:
                raise Exception("Work appears to already exist")
        
        # Make the work source
        self.work_source = WorkSource()
        
        # Save the source of the document
        self.work_source.source = "bereanbible.com"
        self.work_source.resource = os.path.basename(file_name)
        self.work_source.work = self.work
        self.work_source.description = "The Holy Bible, Berean Study Bible, BSB\nCopyright ©2016, 2018 by Bible Hub\nUsed by Permission. All Rights Reserved Worldwide.\n\nhttps://bereanbible.com/"
        self.work_source.save()
        
        # Initialize a couple more things...
        f = None # The file handle
        line_number = 0 # The line number
        
        try:
            
            # Open the file
            f = open(file_name, encoding="iso-8859-1")
            
            # Process each line
            for line in f:
                
                # Note the line number we are importing
                line_number = line_number + 1
                
                # If we are importing starting from a particular line number, then skip lines until you get to this point
                if start_line_number is not None and line_number < start_line_number:
                    pass # Skip this line
                
                else:
                    # Import the line
                    obj = self.import_line(line)
                    
                    if return_created_objects:
                        if obj is not None:
                            objects.append(obj)
                    else:
                        objects = objects + 1
        finally:
            if f is not None:
                f.close()
    
        logger.info("Import complete, duration=%i", time() - start_time )

        return objects

    def import_line(self, line):
        book, chapter, verse_number, text = self.parse_line(line)

        if book is None:
            return
            # Skip this line

        made_book = False

        # Create the book if necessary (if None or for a different book)
        if self.current_book_division is None or self.current_book_division.descriptor != book:
            self.current_book_division = self.make_division(book, self.current_book_division, save=False)
            self.current_book_division.title = book
            self.current_book_division.level = 1
            self.current_book_division.type = "Book"
            self.current_book_division.save()
            made_book = True

        # Create the chapter if necessary
        if self.current_chapter_division is None or self.current_chapter_division.descriptor != chapter or made_book:
            self.current_chapter_division = self.make_division(chapter, self.current_chapter_division, save=False)
            self.current_chapter_division.title = chapter
            self.current_chapter_division.level = 2
            self.current_chapter_division.type = "Chapter"
            self.current_chapter_division.parent_division = self.current_book_division
            self.current_chapter_division.save()

        # Make the verse
        verse = self.make_verse(self.current_verse, self.current_chapter_division, save=False)
        verse.indicator = verse_number
        verse.content = language_tools.normalize_unicode(text.strip())
        verse.save()
        
        self.verses_created = self.verses_created + 1
        logger.info('Successfully imported verse of work, verse_count=%i, title="%s"', self.verses_created, self.work.title) 

    @classmethod
    def parse_line(cls, line):
        r = re.compile('([a-zA-Z0-9 ]+)([0-9]+)([:]([0-9])*)?\t(.*)')

        match = r.match(line)

        if(match):
            groups = match.groups()

            book = groups[0].strip()
            chapter = groups[1]
            verse = groups[3]
            text = groups[4]

            return book, chapter, verse, text

        return None, None, None, line
