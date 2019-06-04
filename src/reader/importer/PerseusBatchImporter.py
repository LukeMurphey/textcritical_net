'''
Created on Oct 11, 2012

@author: Luke
'''

import os
import logging
import csv
import pprint
from time import time
from xml.dom.minidom import parse
from reader.importer.Perseus import PerseusTextImporter
from reader.models import Work
from reader.importer.batch_import import ImportTransforms
from copy import copy

# Get an instance of a logger
logger = logging.getLogger(__name__)

class PerseusFileProcessor():
    """
    This class provides mechanisms for visiting a series of Perseus files and performing batch operations on them.
    """
    
    def __init__(self, perseus_directory, book_selection_policy=None):
        self.perseus_directory = perseus_directory
        self.book_selection_policy = book_selection_policy
        
    def get_title(self, document_xml):
        """
        Get the title of the work.
        """
        
        tei_header_nodes = document_xml.getElementsByTagName("teiHeader")
        
        if len(tei_header_nodes) > 0:
            return PerseusTextImporter.get_title_from_tei_header(tei_header_nodes[0])
        else:
            logger.debug("No TEI header found, title could not be retrieved")
    
    def get_author(self, document_xml):
        """
        Get the author of the work.
        """
        
        return PerseusTextImporter.get_author(document_xml)
    
    def get_editor(self, document_xml):
        """
        Get the editor of the work. Will only return the first editor if there is more than one.
        """
        
        editors = PerseusTextImporter.get_editors(document_xml)
        
        if editors is not None and len(editors) > 0:
            return editors[0]
    
    def get_language(self, document_xml):
        """
        Get the language of the work.
        """
        
        return PerseusTextImporter.get_language(document_xml)
    
    def get_processing_parameters(self, document_xml, file_path, title, author, language, editor):
        """
        Get the processing parameters associated with the given work.
        """
                
        logger.debug("Analyzing %s by %s (%s) to determine if it ought to be imported" % (title, author, language ) )
        
        return self.book_selection_policy( document=document_xml, title=title, author=author, language=language, file_path=file_path, editor=editor )
    
    def __process_file__(self, file_path):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        
        Returns a boolean indicating if the file was imported
        
        Arguments:
        file_path -- The path to the file to import
        """
        
        # Don't try to process files that are not XML
        if not file_path.endswith(".xml"):
            return
        
        # Get the document XML
        document_xml = parse(file_path)
        
        try:
            # Get the information we need to get the import policy
            title = self.get_title(document_xml)
            author = self.get_author(document_xml)
            language = self.get_language(document_xml)
            editor = self.get_editor(document_xml)
            
            return self.process_file(file_path, document_xml, title, author, language, editor)
        finally:
            document_xml.unlink() 
            del(document_xml)

    def process_file(self, file_path, document_xml, title, author, language, editor, **kwargs):
        """
        Process a Perseus file.
        
        Arguments:
        file_path -- The path to the file to import
        document_xml -- The document XML
        title -- The title of the document
        author -- the author of the document
        language -- The language of the document
        editor -- The first editor of the document
        """
        
        raise Exception("Not implemented!")
    
    def set_up(self):
        pass
    
    def tear_down(self):
        pass
    
    def process_directory(self, directory=None, dont_stop_on_errors=True):
        """
        Examine the provided directory and import the files that match the policy.
        """
        
        # Use the directory assigned in the constructor if one is not provided
        if directory is None:
            directory = self.perseus_directory
            
        #logger.debug("Analyzing directory for files to process, directory=%s", directory )
        
        # Keep a count of the files imported
        files_processed = 0
        files_not_processed_due_to_errors = 0
        
        self.set_up()
        
        try:
            # Walk the directory and import the files
            for root, dirs, files in os.walk(directory):
                
                # Process each file
                for f in files:
                    try:
                        # Don't process the "__cts__.xml" files since these are just meta-data files included with the https://opengreekandlatin.github.io/First1KGreek/ project
                        if f != "__cts__.xml" and self.__process_file__( os.path.join( root, f) ):
                            files_processed = files_processed + 1
                            
                    except Exception:
                        logger.exception('Exception generated when attempting to process file="%s"', f)
                        
                        files_not_processed_due_to_errors = files_not_processed_due_to_errors + 1
                        
                        if not dont_stop_on_errors:
                            raise
        finally:
            self.tear_down()
        
        return files_processed, files_not_processed_due_to_errors

class PerseusDataGatherer(PerseusFileProcessor):
    
    def __init__(self, perseus_directory, output_file="perseus_stats.csv", book_selection_policy=None):
        self.perseus_directory = perseus_directory
        self.output_file = output_file
        
        self.book_selection_policy = book_selection_policy
        
    def set_up(self):
        
        if self.output_file is not None:
            self.output_file_h = open(self.output_file, 'wb')
            self.csv_writer = csv.writer(self.output_file_h)
            self.csv_writer.writerow( [ "title", "author", "language", "file" ] )
        else:
            self.output_file_h = None
            self.csv_writer = None
    
    def tear_down(self):
        
        if self.output_file_h is not None:
            self.output_file_h.close()

        
    def process_file(self, file_path, document_xml, title, author, language, editor, **kwargs):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        
        Returns a boolean indicating if the file was imported
        
        Arguments:
        file_path -- The path to the file to import
        document_xml -- The document XML
        title -- The title of the document
        author -- The author of the document
        language -- The language of the document
        editor -- The first editor of the document
        """
        
        processing_parameters = self.get_processing_parameters(document_xml, file_path, title, author, language, editor)
        
        # Get the transforms to be executed
        if processing_parameters is not None and processing_parameters is not False:
            
            if self.csv_writer is not None:
                self.csv_writer.writerow( [ title, author, language, file_path, editor ] )
                
            return True
        
        else:
            return False
        
    def get_stats(self, directory=None, dont_stop_on_errors=True):
        self.process_directory(directory, dont_stop_on_errors)
        
class PerseusBatchImporter(PerseusFileProcessor):
    """
    A batch importer for walking a directory and importing all of the files if they match an import policy.
    """
    
    def __init__(self, perseus_directory, overwrite_existing=False, book_selection_policy=None, import_even_if_already_existing=True, test=False):
        self.perseus_directory = perseus_directory
        self.overwrite_existing = overwrite_existing
        self.book_selection_policy = book_selection_policy
        self.test = test
        
        self.import_even_if_already_existing = import_even_if_already_existing
    
    def does_work_exist(self, title, author, language):
        """
        Determines if the given work already exists.
        """
        
        works = Work.objects.filter( title=title, authors__name=author, language=language)
        
        return works.count() > 0

    def process_file(self, file_path, document_xml, title, author, language, editor, **kwargs):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        
        Returns a boolean indicating if the file was imported
        
        Arguments:
        file_path -- The path to the file to import
        document_xml -- The document XML
        title -- The title of the document
        author -- the author of the document
        language -- The language of the document
        editor -- The first editor of the document
        """
        
        perseus_importer = None
        import_parameters = self.get_processing_parameters(document_xml, file_path, title, author, language, editor)
        
        if self.test:
            pp = pprint.PrettyPrinter(indent=4)
            print "Import policy matched: file_path=%s, title=%s, author=%s, language=%s, editor=%s" % (file_path, title, author, language, editor)
            pp.pprint(import_parameters)
            return

        # Get the transforms to be executed
        if import_parameters not in [None, True, False] and 'transforms' in import_parameters:
            transforms = import_parameters.get('transforms', None)
            
            # Create a copy since we are going to delete items from this one
            import_parameters = copy(import_parameters)
            
            # Delete the transforms because the importer constructor doesn't take this argument
            del import_parameters['transforms']
        else:
            transforms = None
        
        if not self.import_even_if_already_existing and self.overwrite_existing == False and self.does_work_exist(title, author, language):
            logger.info( 'Work already exists, skipping it, title="%s"', title)
            
        elif import_parameters in [None, False]:
            # We are not going to import this work
            pass
        
        elif import_parameters is True:
            # Import this work
            logger.info( 'Importing a Perseus XML file, file_path="%s"', file_path)
            perseus_importer = PerseusTextImporter(overwrite_existing=self.overwrite_existing)
            perseus_importer.import_file(file_path)
        else:
            logger.info( 'Importing a Perseus XML file, file_path="%s"', file_path)
            
            if import_parameters is False:
                perseus_importer = PerseusTextImporter(overwrite_existing=self.overwrite_existing)
            else:
                perseus_importer = PerseusTextImporter(overwrite_existing=self.overwrite_existing, **import_parameters)
            
            perseus_importer.import_file(file_path)
            
        if perseus_importer is not None and perseus_importer.work is not None:
            
            # Run the transforms
            if transforms is not None:
                logger.debug("Running transforms")
                ImportTransforms.run_transforms(perseus_importer.work, transforms)
            else:
                logger.debug("No transforms found")
            
            logger.info('Successfully imported work title="%s", work.id=%i', perseus_importer.work.title_slug, perseus_importer.work.id)
            return True
        
        else:
            return False
        
    def count_files(self, directory=None, dont_stop_on_errors=True):
        
        # Use the directory assigned in the constructor if one is not provided
        if directory is None:
            directory = self.perseus_directory
            
        # Keep a count of the files imported
        files_to_import = 0
        errors          = 0
        
        # Walk the directory and import the files
        for root, dirs, files in os.walk(directory):
            
            # Process each file
            for f in files:
                try:
                    
                    # Get the document XML
                    file_path =  os.path.join( root, f)
                    document_xml = parse(file_path)
                    
                    # Get the information we need to get the import policy
                    title = self.get_title(document_xml)
                    author = self.get_author(document_xml)
                    language = self.get_language(document_xml)
                    
                    if self.get_processing_parameters(document_xml, file_path, title, author, language) is not None:
                        files_to_import = files_to_import + 1
                        
                except Exception:
                    logger.exception('Exception generated when attempting to examine file for import, file="%s"', f)
                    
                    errors = errors + 1
                    
                    if not dont_stop_on_errors:
                        raise
                    
        return files_to_import, errors
        
    def do_import(self, directory=None, dont_stop_on_errors=True):
        """
        Examine the provided directory and import the files that match a policy.
        """
        
        # Use the directory assigned in the constructor if one is not provided
        if directory is None:
            directory = self.perseus_directory
            
        logger.debug("Analyzing directory for files to import, directory=%s", directory )
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        # Process the directory
        files_imported, files_not_imported_due_to_errors = self.process_directory(directory, dont_stop_on_errors)
        
        logger.info("Import complete, files_imported=%i, import_errors=%i, duration=%i", files_imported, files_not_imported_due_to_errors, time() - start_time )
        
        return files_imported