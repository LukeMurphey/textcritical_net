import os
import re
from xml.dom.minidom import Document
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify

from reader.models import Author, Work, WorkSource, Verse, Division
from xml.dom import minidom

# Get an instance of a logger
logger = logging.getLogger(__name__)

class LineNumber():
    """
    Represents a line number in a document.
    """
    
    NUMBER_RE = re.compile(r"(?P<pre>.*?)(?P<number>[0-9]+)(?P<post>.*)")
    
    def __init__(self, value=None, number=0):
        self.pre = None
        self.post = None
        self.number = number
        
        if value is not None:
            self.set(value)
    
    def copy(self):
        """
        Create a copy.
        """
        
        new_line_number = LineNumber()
        
        new_line_number.pre = self.pre
        new_line_number.post = self.post
        new_line_number.number = self.number
        
        return new_line_number
    
    def set(self, value):
        """
        Setteh value of the line number based on the provided string.
        """
        
        r = LineNumber.NUMBER_RE.search(value)
        d = r.groupdict()
        
        self.pre    = d["pre"]
        self.number = int(d["number"])
        self.post   = d["post"]
        
    def __str__(self):
        """
        Return the line number as a string.
        """
        
        if self.pre is None:
            pre = ""
        else:
            pre = self.pre
        
        if self.post is None:
            post = ""
        else:
            post = self.post
        
        return "%s%i%s" % (pre, self.number, post)

    def increment(self):
        """
        Increment the line number
        """
        
        self.number = self.number + 1

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
            
            self.line_number_end = LineNumber()
            self.line_number_start = LineNumber()
            
            self.levels = {}
            
            self.custom_attributes = {}
            
        def get_custom_attribute(self, name, default_value=None):
            return self.custom_attributes.get(name, default_value)
        
        def set_custom_attribute(self, name, value):
            self.custom_attributes[name] = value
            
        def increment_division_level(self, level, count=1):
            if level in self.levels:
                self.levels[level] = self.levels[level] + count
            else:
                self.levels[level] = count
            
        def get_division_level_count(self, level):
            return self.levels.get(level, 0)
            
        def increment_line_count(self):
            self.line_number_end.increment()
        
        def reset_start_line_count(self):
            self.line_number_start = self.line_number_end.copy()
            self.line_number_start.increment()
            
        def get_line_count_title(self):
            
            if self.line_number_start.number == 0:
                self.line_number_start.number = 1
            
            return "lines %s-%s" % ( str(self.line_number_start), str(self.line_number_end) )
            
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
            
            ret = TextImporter.copy_node(src_node, self.document, dst_node, copy_attributes=True, copy_children=False)
                
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
    def copy_node(src_node, dst_doc, dst_node, copy_attributes=True, copy_children=False, concatenate_child_text_nodes=True, handle_inappropriate_text_node_children=True):
        """
        Copy a node from one document to another and returns the newly created node.
        
        Arguments:
        src_node -- The node to copy
        dst_doc -- The document to copy the node to
        dst_node -- The location to copy the node under
        copy_attributes -- Determines if the attributes ought to be copied
        copy_children -- Determines if the children from the src_node will be copied
        concatenate_child_text_nodes -- If true, then the contents of a text node will be attached to the destination node if both are text nodes
        handle_inappropriate_text_node_children -- If true, then this function will attempt to recover nicely from the attempt to attach a node under a text node by attaching the node to the text node's parent
        """
        
        # Make the copy of the node
        if copy_attributes and copy_children:
            new_node = dst_doc.importNode(src_node, True)
        
        elif src_node.nodeType == minidom.Element.TEXT_NODE:
            new_node = dst_doc.createTextNode(src_node.data)
            
        else:
            new_node = dst_doc.createElement(src_node.tagName)
            
            # Copy attributes
            if copy_attributes:
                for name, value in src_node.attributes.items():
                    new_node.setAttribute(name, value)
                
        # Append the content
        if dst_node is not None:
            
            # If both are text nodes, then attach the content if allowed
            if concatenate_child_text_nodes and src_node.nodeType == minidom.Element.TEXT_NODE and dst_node.nodeType == minidom.Element.TEXT_NODE:
                dst_node.data = dst_node.data + src_node.data
                new_node = dst_node
                
            # If this is an attempt to attach a node to a text node, then fit this node at the same level as the text node
            elif handle_inappropriate_text_node_children and dst_node.nodeType == minidom.Element.TEXT_NODE:
                dst_node.parentNode.appendChild(new_node)
                
            # Attach the node as a child of the destination
            else:
                dst_node.appendChild(new_node)
        else:
            logger.error("Destination node is null")
        
        return new_node
    
    def make_division(self, descriptor, current_division=None, save=True):
        
        # Determine the sequence number (used for division ordering)
        if current_division is None:
            num = 1
        else:
            num = current_division.sequence_number + 1
        
        # Make the chapter
        division = Division()
        division.sequence_number = num
        division.descriptor = descriptor
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
            logger.info("Marking division as a readable unit because it contains a verse, division=%s", division.descriptor)
        
        if save:
            verse.save()
        
        return verse
    
    def make_author(self, name, save_if_new=True):
        
        # If the name is none, then assume the user is unknown
        if name is None or len(name.strip()) == 0:
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
        slug_was_already_taken = False
        
        while Work.objects.filter(title_slug=work.title_slug).count() > 0:
            slug_was_already_taken = True
            work.title_slug = slugify(work.title) + "-" + str(i)
            i = i + 1  
            
        # Make a log message noting that the slug title was already taken
        if slug_was_already_taken:
            logger.info("The slug for the given work was already used so another was assigned, title=%s, new_slug=%s", work.title, work.title_slug)
            
        self.work = work
        return work
    
    def import_file(self, file_name):
        raise Exception("not implemented")
    
    def import_directory( self, dir_name ):
        
        dir_list =os.listdir(dir_name)
        
        for file_name in dir_list:
            self.import_file( file_name )
            
    
            
    