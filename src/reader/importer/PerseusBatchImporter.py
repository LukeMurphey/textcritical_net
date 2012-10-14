'''
Created on Oct 11, 2012

@author: Luke
'''

import os
import json
import logging
from xml.dom.minidom import parse
from reader.importer.Perseus import PerseusTextImporter
from reader.models import Work

# Get an instance of a logger
logger = logging.getLogger(__name__)

class WorkDescriptor():
    """
    Represents a work and allows for filtering in order to define import parameters for the work.
    """
    
    def __init__(self, author=None, title=None, file_name=None, language=None, import_parameters=None, **kwargs):
        self.author = author
        self.title = title
        self.file_name = file_name
        self.language = language
        self.import_parameters = import_parameters
        
    def rejects(self, field_filter, item):
        """
        Determines if the work descriptor does not match the work based on the field provided.
        """
        
        if field_filter is not None and item != field_filter:
            return True
        else:
            return False
        
    def should_be_imported(self, author, title, file_path, language):
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
                    logger.debug("Successfuly executed transforms with arguments, transform=%s", fx_name)
                else:
                    fx(work=work)
                    logger.debug("Successfuly executed transforms without arguments, transform=%s", fx_name)
                    
            else:
                logger.warn("Transform function could not be found, transform=%s", fx_name)
        

class JSONImportPolicy():
    """
    This class represents a selection policy 
    """
    
    def __init__(self):
        self.descriptors = []
    
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
    
    def should_be_imported(self, author=None, title=None, language=None, file_path=None, **kwargs ):
        """
        Indicates if the work denoted by the provided parameters ought to be imported. Returns true or import
        parameters if it ought to be imported.
        """
        
        # Go through each descriptor until one returns non-none (which indicates that is supports importing)
        for desc in self.descriptors:
            
            return_value = desc.should_be_imported( author, title, file_path, language )
        
            if return_value is not None:
                return return_value

class PerseusBatchImporter():
    """
    A batch importer for walking a directory and importing all of the files if they match an import policy.
    """
    
    def __init__(self, perseus_directory, overwrite_existing=False, book_selection_policy=None):
        self.perseus_directory = perseus_directory
        self.overwrite_existing = overwrite_existing
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
    
    def get_import_parameters(self, document_xml, file_path, title, author, language):
        """
        Get the language of the work.
        """
                
        logger.debug("Analyzing %s by %s (%s) to determine if it ought to be imported" % (title, author, language ) )
        
        return self.book_selection_policy( document=document_xml, title=title, author=author, language=language, file_path=file_path )
    
    def does_work_exist(self, title, author, language):
        """
        Determines if the given work already exists.
        """
        
        works = Work.objects.filter( title=title, authors__name=author, language=language)
        
        return works.count() > 0
    
    def process_file(self, file_path):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        """
        
        # Get the document XML
        document_xml = parse(file_path)
        
        # Get the information we need to get the import policy
        title = self.get_title(document_xml)
        author = self.get_author(document_xml)
        language = self.get_language(document_xml)
        
        perseus_importer = None
        import_parameters = self.get_import_parameters(document_xml, file_path, title, author, language)
        
        # Get the transforms to be executed
        if import_parameters is not None and 'transforms' in import_parameters:
            transforms = import_parameters.get('transforms', None)
            del import_parameters['transforms']
        else:
            transforms = None
        
        if self.overwrite_existing == False and self.does_work_exist(title, author, language):
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
            
        if perseus_importer is not None:
            
            # Run the transforms
            if transforms is not None:
                logger.debug("Running transforms")
                ImportTransforms.run_transforms(perseus_importer.work, transforms)
            else:
                logger.debug("No transforms found")
            
            logger.info('Successfully imported work title="%s", work.id=%i', perseus_importer.work.title_slug, perseus_importer.work.id)
    
    def do_import(self, directory=None):
        """
        Examine the provided directory and import the files that match a policy.
        """
        
        # Use the directory assigned in the constructor if one is not provided
        if directory is None:
            directory = self.perseus_directory
            
        logger.debug("Analyzing %s for files to import", directory )
        
        # Walk the directory and import the files
        for root, dirs, files in os.walk(directory):
            
            # Process each file
            for f in files:
                self.process_file( os.path.join( root, f) )