from reader.models import Division, Verse, Work
from django.template.defaultfilters import slugify
import logging
import re
import os
import json

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
    
    def __init__(self, author=None, title=None, file_name=None, language=None, import_parameters=None, editor=None, should_import=True, **kwargs):
        self.editor = editor
        self.author = author
        self.title = title
        self.file_name = self.convert_to_re_if_necessary(file_name)
        self.language = language
        self.import_parameters = import_parameters
        self.should_import = should_import
        
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
            
            # If the filter is actually an array (but not a string which looks like an array), then see if the item is in the list
            if ( isinstance(field_filter, list) or isinstance(field_filter, tuple) ) and not isinstance(field_filter, basestring):
                for i in field_filter:
                    if i == item:
                        return True
            
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
        
    def should_be_processed(self, author, title, file_path, language, editor):
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
        
        if self.rejects(self.editor, editor):
            return None
        
        if self.rejects(self.title, title):
            return None
        
        if self.rejects(self.language, language):
            return None
        
        if not self.should_import:
            return False # This is a dropping rule the prevents importation
        
        if self.import_parameters is not None:
            return self.import_parameters
        else:
            return True

class ImportPolicy():
    
    def __init__(self):
        self.descriptors = []
        
    def should_be_processed(self, author=None, title=None, language=None, file_path=None, editor=None, **kwargs ):
        """
        Indicates if the work denoted by the provided parameters ought to be imported. Returns true or import
        parameters if it ought to be imported.
        """
        
        # Go through each descriptor until one returns non-none (which indicates that is supports importing)
        for desc in self.descriptors:
            
            return_value = desc.should_be_processed( author, title, file_path, language, editor )
        
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

class ImportTransforms():
    
    @staticmethod
    def set_meta_data(work=None, title=None, title_slug=None, language=None, **kwargs):
        changes = 0
        
        if title is not None:
            work.title = title
            changes = changes + 1
            
        if title_slug is not None:
            work.title_slug = title_slug
            changes = changes + 1
            
        if language is not None:
            work.language = language
            changes = changes + 1
            
        if changes > 0:
            work.save()
            
    @staticmethod
    def update_title_slug(work=None, additional_fields=None):
        
        # If fields were not provided then attempt to use the editor field and/or language
        if additional_fields is None:
            
            # Use the editor's name
            if work.editors.count() > 0:
                
                # Get the editor
                editor = work.editors.all()[0].name
                editor = editor.replace("Ph. D.", "").replace("M.A.", "").replace("LL.D.", "").replace("A.M.", "").replace("Esq.", "").replace(",", "").strip().lower()
                
                # Get the last name of the editor
                if " " in editor:
                    editor = editor.split(" ")[-1]
                
                additional_fields = [ slugify(editor) ]
            
            # Otherwise, use the language
            else:
                additional_fields = [ slugify( work.language ) ]
            
        elif not isinstance(additional_fields, (list, tuple)) or isinstance(additional_fields, basestring):
            additional_fields = [additional_fields]
            
        for f in additional_fields:
            
            if not f.startswith("-"):
                f = "-" + f
            
            new_title_slug = slugify(work.title) + f
            
            if Work.objects.filter(title_slug=new_title_slug).count() == 0:
                work.title_slug = new_title_slug
                work.save()
                
                return
            
        logger.warning("Unable to allocate a new title slug based on the fields provided")
    
    
    @staticmethod
    def set_division_title( work=None, existing_division_title_slug=None, existing_division_parent_title_slug=None, existing_division_sequence_number=None, title=None, title_slug=None, descriptor=None, **kwargs):
        
        changes = 0
        
        # Get the division
        division = Division.objects.filter(work=work)
        
        if existing_division_parent_title_slug:
            division = division.filter(parent_division__title_slug=existing_division_parent_title_slug)
        
        if existing_division_title_slug:
            division = division.filter(title_slug=existing_division_title_slug)
            
        if existing_division_sequence_number:
            division = division.filter(sequence_number=existing_division_sequence_number)
            
        # Get the division
        division = division.get()
        
        # Update the title
        if title is not None:
            division.title = title
            changes = changes + 1
            
        # Update the title slug
        if title_slug is not None:
            division.title_slug = title_slug
            changes = changes + 1
            
        # Update the descriptor
        if descriptor is not None:
            division.descriptor = descriptor
            changes = changes + 1
        
        
        if changes > 0:
            division.save()
    
    @staticmethod
    def set_division_readable( work=None, sequence_number=None, title_slug=None, type=None, descriptor=None, level=None, readable=True):
        
        division = Division.objects.filter(work=work)
        
        if sequence_number is not None:
            division = division.filter(sequence_number=sequence_number)
            
        if title_slug is not None:
            division = division.filter(title_slug=title_slug)
            
        if type is not None:
            division = division.filter(type=type)
            
        if descriptor is not None:
            division = division.filter(descriptor=descriptor)
            
        if level is not None:
            division = division.filter(level=level)
            
        division = division.get()
        
        logger.info("Setting division readability, division=%s", division.title_slug)
        division.readable_unit = readable
        division.save()
    
    @staticmethod
    def delete_unnecessary_divisions( work=None, **kwargs):
        
        # Sift through the work and delete divisions that:
        #    * have no verses
        #    * is not a parent to any divisions
        
        divisions = Division.objects.filter(work=work)
        divisions_to_delete = []
        
        for division in divisions:
            
            # Determine if any verses point to the division
            verses_count = Verse.objects.filter(division=division).count()
            
            # Determine if any this division has any sub-divisions
            if verses_count == 0:
                sub_divisions_count = Division.objects.filter(parent_division=division).count()
                
                # No sub-divisions; this one can be deleted
                if sub_divisions_count == 0:
                    divisions_to_delete.append(division)
                    
        # Delete the divisions
        logger.info("Unnecessary divisions are being deleted, count=%i, title=%s", len(divisions_to_delete), work.title)
    
        for division in divisions_to_delete:
            division.delete()
            
        # Return the number of divisions deleted
        return len(divisions_to_delete)
    
    @staticmethod
    def delete_divisions_by_title_slug( work=None, title_slugs=None):
        if title_slugs is None:
            logger.warn("Transform could not be executed because no title_slugs were provided, transform=delete_divisions_by_title_slug")
        else:
            
            # Get the divisions to delete
            divisions = Division.objects.filter(work=work, title_slug__in=title_slugs)
            
            # Log how many divisions will be deleted
            logger.info("Divisions are being deleted, count=%i, title=%s, titles_to_be_deleted=%r", len(divisions), work.title, title_slugs)
            
            for division in divisions:
                
                # Delete the verses
                Verse.objects.filter(division=division).delete()
                
                # Now delete the division
                division.delete()
                
            return len(divisions)
    
    @staticmethod
    def run_transforms( work, transforms ):
        
        fxs = dir(ImportTransforms)
        
        # Execute each of the transform functions
        for fx_name, args in transforms.items():
            
            if not isinstance(args, (list, tuple)):
                args = [args]
                
            for arguments in args:
                
                # Make sure the function is present
                if fx_name in fxs and fx_name != 'run_transforms':
                    
                    # Get the function to call
                    fx = getattr(ImportTransforms, fx_name)
                    
                    # Execute the function
                    if args is not None:
                        fx(work=work, **arguments)
                        logger.debug("Successfully executed transforms with arguments, transform=%s", fx_name)
                    else:
                        fx(work=work)
                        logger.debug("Successfully executed transforms without arguments, transform=%s", fx_name)
                        
                else:
                    logger.warn("Transform function could not be found, transform=%s", fx_name)