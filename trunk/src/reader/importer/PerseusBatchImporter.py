'''
Created on Oct 11, 2012

@author: Luke
'''

import os
import json
from xml.dom.minidom import parse
from reader.importer.Perseus import PerseusTextImporter

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
    
    def __init__(self, perseus_directory, overwrite=False, book_selection_policy=None):
        self.perseus_directory = perseus_directory
        self.overwrite = overwrite
        self.book_selection_policy = book_selection_policy
        
    def get_title(self, document_xml):
        """
        Get the title of the work.
        """
        
        tei_header_nodes = document_xml.getElementsByTagName("teiHeader")
        
        if len(tei_header_nodes) > 0:
            return PerseusTextImporter.get_title_from_tei_header(tei_header_nodes[0])
        else:
            print "No TEI header found"
    
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
    
    def get_import_parameters(self, document_xml, file_path):
        """
        Get the language of the work.
        """
        
        title = self.get_title(document_xml)
        author = self.get_author(document_xml)
        language = self.get_language(document_xml)
        
        print "Analyzing %s by %s (%s) to determine if it ought to be imported" % (title, author, language )
        
        return self.book_selection_policy( document=document_xml, title=title, author=author, language=language, file_path=file_path )
    
    def process_file(self, file_path):
        """
        Determine if the provided file ought to be imported and import it if necessary.
        """
        
        # Get the document XML
        document_xml = parse(file_path)
        
        perseus_importer = None
        import_parameters = self.get_import_parameters(document_xml, file_path)
        
        if import_parameters is None:
            # We are not going to import this work
            pass
        elif import_parameters is True:
            # Import this work
            print "Importing the file: ", file_path
            perseus_importer = PerseusTextImporter()
            perseus_importer.import_file(file_path)
        else:
            print "Importing the file: ", file_path
            perseus_importer = PerseusTextImporter()
            perseus_importer.import_file(file_path, **import_parameters)
            
        if perseus_importer is not None:
            print "Successfully imported work:", perseus_importer.work.title_slug, perseus_importer.work.id
    
    def do_import(self, directory=None):
        """
        Examine the provided directory and import the files that match a policy.
        """
        
        # Use the directory assigned in the constructor if one is not provided
        if directory is None:
            directory = self.perseus_directory
            
        print "Analyzing", directory, "for files to import"
        
        # Walk the directory and import the files
        for root, dirs, files in os.walk(directory):
            
            # Process each file
            for f in files:
                self.process_file( os.path.join( root, f) )