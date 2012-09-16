import os
from django.core.exceptions import ObjectDoesNotExist

from reader.models import Author, Work, WorkSource, Verse, Chapter

class TextImporter():
    
    def __init__(self, work=None, work_source=None):
        
        if work is not None:
            self.work = work
        else:
            self.work = Work()
            
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
            
        return new_node
    
    def make_chapter(self, current_chapter=None, save=True):
        
        # Determine the sequence number (used for chapter ordering)
        if current_chapter is None:
            num = 1
        else:
            num = current_chapter.sequence_number + 1
        
        # Make the chapter
        chapter = Chapter()
        chapter.sequence_number = num
        chapter.indicator = str(num)
        chapter.work = self.work
        
        if save:
            chapter.save()
        
        return chapter
    
    def make_verse(self, current_verse=None, chapter=None, save=True):
        
        # Determine the sequence number (used for verse ordering)
        if current_verse is None:
            num = 1
        else:
            num = current_verse.sequence_number + 1
                
        # Make the verse
        verse = Verse()
        verse.sequence_number = num
        verse.chapter = chapter
        
        if save:
            verse.save()
        
        return verse
    
    def make_author(self, name, save_if_new=True):
        
        try:
            author = Author.objects.get(name=name)
        except ObjectDoesNotExist:
            author = Author()
            author.name = name
            
            if save_if_new:
                author.save()
            
        return author
    
    def make_work(self, title):
        
        try:
            work = Work.objects.get(title=title)
        except ObjectDoesNotExist:
            work = Work()
            work.title = title
            
        return work
    
    def import_file(self, file_name):
        raise Exception("not implemented")
    
    def import_directory( self, dir_name ):
        
        dir_list =os.listdir(dir_name)
        
        for file_name in dir_list:
            self.import_file( file_name )
            
    
            
    