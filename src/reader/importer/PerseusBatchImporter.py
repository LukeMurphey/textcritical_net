'''
Created on Oct 11, 2012

@author: Luke
'''

import os
import json
import logging
import csv
import re
from time import time
from xml.dom.minidom import parse
from reader.importer.Perseus import PerseusTextImporter
from reader.models import Work

# Get an instance of a logger
logger = logging.getLogger(__name__)

def wildcard_to_re( wildcard_str ):
    """
    Take a wildcarded string (like "tree*") and create a regular expression for it.
    
    Arguments:
    wildcard_str -- A string which represents a wildcard
    """
    
    # Split by the * and put the pieces back together as a wildcard
    wc_split = wildcard_str.split("*")
    
    wc_re = ""
    
    for s in wc_split:
        wc_re = wc_re + ".*" + re.escape(s)
    
    return re.compile(wc_re)

class WorkDescriptor():
    """
    Represents a work and allows for filtering in order to define import parameters for the work.
    """
    
    def __init__(self, author=None, title=None, file_name=None, language=None, import_parameters=None, **kwargs):
        self.author = author
        self.title = title
        self.file_name = self.convert_to_re_if_necessary(file_name)
        self.language = language
        self.import_parameters = import_parameters
        
    def convert_to_re_if_necessary(self, wildcard):
        """
        Convert the provided string which may be an wildcard to an re. If it is a wildcard (contains a *) then a re will be
        returned. Otherwise, the item will be returned unchanged.
        
        Arguments:
        wildcard -- The item that may be a wildcard which ought to be converted to an re
        """
        
        if wildcard is None:
            return None
        elif wildcard.find("*") >= 0:
            return wildcard_to_re(wildcard)
        else:
            return wildcard
        
    def matches(self, field_filter, item):
        """
        Determine if the given item matches the provided field filter. The field_filter can be a str or an re.
        
        Arguments:
        field_filter -- A string or an an object that declares a match function (which takes an str)
        item -- The item to be determined if it matches
        """
        
        try:
            return field_filter.match(item)
        except AttributeError:
            return field_filter == item
            
    def rejects(self, field_filter, item):
        """
        Determines if the work descriptor does not match the work based on the field provided.
        
        Arguments:
        field_filter -- A string or an an object that declares a match function (which takes an str)
        item -- The item to be determined if it matches
        """
        
        if field_filter is not None and not self.matches( field_filter, item ):
            return True
        else:
            return False
        
    def should_be_processed(self, author, title, file_path, language):
        """
        Determines if the work ought to be imported and provides the import parameters or
        true if it ought to be.
        """
        
        # Get the file_name
        file_name = os.path.basename(file_path)
        
        if self.rejects(self.file_name, file_name):
            return None
        
        if self.rejects(self.author, author):
            return None
        
        if self.rejects(self.title, title):
            return None
        
        if self.rejects(self.language, language):
            return None
        
        if self.import_parameters is not None:
            return self.import_parameters
        else:
            return True

class ImportTransforms():
    
    @staticmethod
    def set_meta_data(work=None, title=None, title_slug=None, **kwargs):
        changes = 0
        
        if title is not None:
            work.title = title
            changes = changes + 1
            
        if title_slug is not None:
            work.title_slug = title_slug
            changes = changes + 1
            
        if changes > 0:
            work.save()
        
    @staticmethod
    def run_transforms( work, transforms ):
        
        fxs = dir(ImportTransforms)
        
        # Execute each of the transform functions
        for fx_name, args in transforms.items():
            
            # Make sure the function is present
            if fx_name in fxs and fx_name != 'run_transforms':
                
                # Get the function to call
                fx = getattr(ImportTransforms, fx_name)
                
                # Execute the function
                if args is not None:
                    fx(work=work, **args)
                    logger.debug("Successfully executed transforms with arguments, transform=%s", fx_name)
                else:
                    fx(work=work)
                    logger.debug("Successfully executed transforms without arguments, transform=%s", fx_name)
                    
            else:
                logger.warn("Transform function could not be found, transform=%s", fx_name)
        
class ImportPolicy():
    
    def __init__(self):
        self.descriptors = []
        
    def should_be_processed(self, author=None, title=None, language=None, file_path=None, **kwargs ):
        """
        Indicates if the work denoted by the provided parameters ought to be imported. Returns true or import
        parameters if it ought to be imported.
        """
        
        # Go through each descriptor until one returns non-none (which indicates that is supports importing)
        for desc in self.descriptors:
            
            return_value = desc.should_be_processed( author, title, file_path, language )
        
            if return_value is not None:
                return return_value

class JSONImportPolicy(ImportPolicy):
    """
    This class represents a selection policy 
    """
    
    def load_policy(self, file_name):
        """
        Load the policy from the given JSON file.
        """
        
        # Get the file into a string
        fh = open(file_name, 'r')
        file_string = fh.read()
        fh.close()
        
        # Load the file into JSON
        policy_entries = json.loads( file_string )
        
        descriptors = []
        
        for entry in policy_entries:
            descriptors.append( WorkDescriptor(**entry) )
            
        # Save the descriptors
        self.descriptors = descriptors

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
        
        tei_header_nodes = document_xml.getElementsByTagName("teiHeader")
        
        if len(tei_header_nodes) > 0:
            bibl_struct_nodes = tei_header_nodes[0].getElementsByTagName("biblStruct")
        
            if len(bibl_struct_nodes) > 0:
                return PerseusTextImporter.get_author_from_bibl_struct(bibl_struct_nodes[0])
    
    def get_language(self, document_xml):
        """
        Get the language of the work.
        """
        
        return PerseusTextImporter.get_language(document_xml)
    
    def get_processing_parameters(self, document_xml, file_path, title, author, language):
        """
        Get the language of the work.
        """
                
        logger.debug("Analyzing %s by %s (%s) to determine if it ought to be imported" % (title, author, language ) )
        
        return self.book_selection_policy( document=document_xml, title=title, author=author, language=language, file_path=file_path )
        
    
    def __process_file__(self, file_path):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        
        Returns a boolean indicating if the file was imported
        
        Arguments:
        file_path -- The path to the file to import
        """
        
        # Get the document XML
        document_xml = parse(file_path)
        
        try:
            # Get the information we need to get the import policy
            title = self.get_title(document_xml)
            author = self.get_author(document_xml)
            language = self.get_language(document_xml)
            
            return self.process_file(file_path, document_xml, title, author, language)
        finally:
            document_xml.unlink() 
            del(document_xml)
        
    def process_file(self, file_path, document_xml, title, author, language, **kwargs):
        """
        Process a Perseus file.
        
        Arguments:
        file_path -- The path to the file to import
        document_xml -- The document XML
        title -- The title of the document
        author -- the author of the document
        language -- The language of the document
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
            
        logger.debug("Analyzing directory for files to processing, directory=%s", directory )
        
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
                        if self.__process_file__( os.path.join( root, f) ):
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

        
    def process_file(self, file_path, document_xml, title, author, language, **kwargs):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        
        Returns a boolean indicating if the file was imported
        
        Arguments:
        file_path -- The path to the file to import
        document_xml -- The document XML
        title -- The title of the document
        author -- the author of the document
        language -- The language of the document
        """
        
        processing_parameters = self.get_processing_parameters(document_xml, file_path, title, author, language)
        
        # Get the transforms to be executed
        if processing_parameters is not None:
            
            if self.csv_writer is not None:
                self.csv_writer.writerow( [ title, author, language, file_path ] )
                
            return True
        
        else:
            return False
        
    def get_stats(self, directory=None, dont_stop_on_errors=True):
        self.process_directory(directory, dont_stop_on_errors)
        
class PerseusBatchImporter(PerseusFileProcessor):
    """
    A batch importer for walking a directory and importing all of the files if they match an import policy.
    """
    
    def __init__(self, perseus_directory, overwrite_existing=False, book_selection_policy=None, import_even_if_already_existing=True):
        self.perseus_directory = perseus_directory
        self.overwrite_existing = overwrite_existing
        self.book_selection_policy = book_selection_policy
        
        self.import_even_if_already_existing = import_even_if_already_existing
    
    def does_work_exist(self, title, author, language):
        """
        Determines if the given work already exists.
        """
        
        works = Work.objects.filter( title=title, authors__name=author, language=language)
        
        return works.count() > 0
    
    def process_file(self, file_path, document_xml, title, author, language, **kwargs):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        
        Returns a boolean indicating if the file was imported
        
        Arguments:
        file_path -- The path to the file to import
        document_xml -- The document XML
        title -- The title of the document
        author -- the author of the document
        language -- The language of the document
        """
        
        perseus_importer = None
        import_parameters = self.get_processing_parameters(document_xml, file_path, title, author, language)
        
        # Get the transforms to be executed
        if import_parameters not in [None, True, False] and 'transforms' in import_parameters:
            transforms = import_parameters.get('transforms', None)
            del import_parameters['transforms']
        else:
            transforms = None
        
        if not self.import_even_if_already_existing and self.overwrite_existing == False and self.does_work_exist(title, author, language):
            logger.info( 'Work already exists, skipping it, title="%s"', title)
            
        elif import_parameters is None:
            # We are not going to import this work
            pass
        
        elif import_parameters is True:
            # Import this work
            logger.info( 'Importing a Perseus XML file, file_path="%s"', file_path)
            perseus_importer = PerseusTextImporter(overwrite_existing=self.overwrite_existing)
            perseus_importer.import_file(file_path)
        else:
            logger.info( 'Importing a Perseus XML file, file_path="%s"', file_path)
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