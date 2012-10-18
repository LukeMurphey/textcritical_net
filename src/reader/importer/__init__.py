import os
from xml.dom.minidom import Document
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify

from reader.models import Author, Work, WorkSource, Verse, Division

# Get an instance of a logger
logger = logging.getLogger(__name__)

class TextImporter():
    
    class ImportContext():
        """
        Represents the context that used during the process of importing. This is necessary so that
        the verse are associated with the correct books and chapters.
        """
        
        def __init__(self, tag_name, book=None, division=None, verse=None):
            self.book = book
            self.division = division
            self.verse = verse
            self.tag_name = tag_name
            
            self.document = None
            self.initialize_xml_doc(tag_name)
            
            self.divisions = []
            
        def initialize_xml_doc(self, tag_name=None):
            
            if tag_name is None:
                tag_name = self.tag_name
            
            self.document = Document()
            
            self.current_node = self.document.createElement(tag_name)
            
            self.document.appendChild(self.current_node)
            
            return self.document
        
        def append_xml(self, src_node, dst_node):
            
            #if self.document is None:
            #    self.initialize_xml_doc()
            
            if dst_node is None:
                dst_node = self.current_node
                
            """
            if log:
                if src_node.nodeType != src_node.TEXT_NODE:
                    logger.debug("Attaching %r to %r" % (src_node.tagName, dst_node.tagName))
                
                else:
                    logger.debug("Attaching %r to %r" % (src_node.data, dst_node.tagName))
            """
             
            ret = TextImporter.copy_node(src_node, self.document, dst_node, copy_attributes=True, copy_children=False)
            
            """
            if log:
                logger.debug("XML is " + self.document.toxml())
            """
                
            return ret
                
            
    def __init__(self, work=None, work_source=None):
        
        if work is not None:
            self.work = work
        else:
            self.work = None
            
        if work_source is not None:
            self.work_source = work_source
        else:
            self.work_source = WorkSource()
    
    @staticmethod
    def copy_node(src_node, dst_doc, dst_node, copy_attributes=True, copy_children=False):
        """
        Copy a node from one document to another and returns the newly created node.
        
        Arguments:
        src_node -- The node to copy
        dst_doc -- The document to copy the node to
        dst_node -- The location to copy the node under
        copy_attributes -- Determines if the attributes ought to be copied
        copy_children -- Determines if the children from the src_node will be copied
        """
        
        if copy_attributes and copy_children:
            new_node = dst_doc.importNode(src_node, True)
        
        elif src_node.nodeType == src_node.TEXT_NODE:
            new_node = dst_doc.createTextNode(src_node.data)
            
        else:
            new_node = dst_doc.createElement(src_node.tagName)
            
            # Copy attributes
            if copy_attributes:
                for name, value in src_node.attributes.items():
                    new_node.setAttribute(name, value)
                
        if dst_node is not None:
            dst_node.appendChild(new_node)
        else:
            logger.error("Destination node is null")
        
        return new_node
    
    def make_division(self, current_division=None, save=True):
        
        # Determine the sequence number (used for division ordering)
        if current_division is None:
            num = 1
        else:
            num = current_division.sequence_number + 1
        
        # Make the chapter
        division = Division()
        division.sequence_number = num
        division.indicator = str(num)
        division.work = self.work
        
        if save:
            division.save()
        
        return division
    
    def make_verse(self, current_verse=None, division=None, save=True):
        
        # Determine the sequence number (used for verse ordering)
        if current_verse is None:
            num = 1
        else:
            num = current_verse.sequence_number + 1
                
        # Make the verse
        verse = Verse()
        verse.sequence_number = num
        verse.division = division
        
        if division is not None and division.readable_unit == False:
            division.readable_unit = True
            division.save()
            logger.info("Marking division as a readable unit because it contains a verse, division=%r", division)
        
        if save:
            verse.save()
        
        return verse
    
    def make_author(self, name, save_if_new=True):
        
        # If the name is none, then assume the user is unknown
        if name is None:
            name = "Unknown"
        
        # Save the author
        try:
            author = Author.objects.get(name=name)
        except ObjectDoesNotExist:
            author = Author()
            author.name = name
            
            if name in ["Unknown", "Various"]:
                author.meta_author = True
            
            if save_if_new:
                author.save()
            
        return author
    
    def make_work(self, title, try_to_get_existing_work=False):
        
        # Try to get the existing work if it exists
        if try_to_get_existing_work:
            try:
                work = Work.objects.get(title=title)
                self.work = work
                return work
            except ObjectDoesNotExist:
                pass
        
        # Create a new work
        work = Work()
        work.title = title
        work.title_slug = slugify(title)
        
        # Set the slug to the next free one if the name is not unique
        i = 1
        while Work.objects.filter(title_slug=work.title_slug).count() > 0:
            work.title_slug = slugify(work.title) + "-" + str(i)
            i = i + 1  
            
        self.work = work
        return work
    
    def import_file(self, file_name):
        raise Exception("not implemented")
    
    def import_directory( self, dir_name ):
        
        dir_list =os.listdir(dir_name)
        
        for file_name in dir_list:
            self.import_file( file_name )
            
    
            
    