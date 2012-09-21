'''
Created on Sep 2, 2012

@author: Luke
'''
from xml.dom.minidom import parse, Document, parseString
import logging
import re

from reader.importer import TextImporter
from reader.models import Author, Work, WorkSource, Verse, Chapter, Section
from reader.language_tools.greek import Greek

from django.db import transaction

# Get an instance of a logger
logger = logging.getLogger(__name__)

class State():
    
    def __init__(self, name, section_type):
        self.section_type = section_type
        self.name = name
        
    def is_chunk(self):
        return self.section_type is not None
        
    @staticmethod
    def createFromStateNode( state_node ):
        
        unit_name = state_node.attributes["unit"].value
            
        if state_node.attributes.get("n", None) != None:
            section_type = state_node.attributes["n"].value
        else:
            section_type = None
            
        return State(unit_name, section_type)
    
    def __str__(self):
        return self.name

class PerseusTextImporter(TextImporter):
    
    DIV_PARSE_REGEX = re.compile( r"div(?P<level>[0-9]+)" )
    
    VERSE_TAG_NAME = "verse"
    CHAPTER_TAG_NAME = "chapter"
    
    class ImportContext():
        """
        Represents the context that used during the process of importing. This is necessary so that
        the verse are associated with the correct books and chapters.
        """
        
        def __init__(self, tag_name, book=None, chapter=None, verse=None, section = None):
            self.book = book
            self.chapter = chapter
            self.verse= verse
            self.section = section
            
            self.initialize_xml_doc(tag_name)
            
            self.chapters = []
            
        def initialize_xml_doc(self, tag_name):
            self.document = Document()
            
            self.current_node = self.document.createElement(tag_name)
            
            self.document.appendChild(self.current_node)
            
            return self.document
        
        def append_xml(self, src_node, dst_node):
            
            if dst_node is None:
                dst_node = self.current_node
                
            return TextImporter.copy_node(src_node, self.document, dst_node, True, False)
            
    def import_xml_string(self, xml_string, state_set=0 ):
        """
        Import the work from the string provided.
        
        Arguments:
        xml_string -- A string representing XML
        state_set -- The state set to use
        """
        
        doc = parseString(xml_string)
        return self.import_xml_document(doc, state_set)
         
    def import_file( self, file_name, state_set=0 ):
        """
        Import the provided XML file.
        
        Arguments:
        file_name -- The file name of a Perseus XML work
        state_set -- The state set to use
        """
        
        # Create the source object so that we remember where we got the file
        #self.work_source = WorkSource()
        #self.work_source.source = "Perseus.tufts.edu"
        #self.work_source.resource = os.path.basename(file_name)
        
        # Import the document
        doc = parse(file_name)
        return self.import_xml_document(doc, state_set)
    
    def make_section(self, level, import_context, section_type=None, title=None, original_title=None):
        
        new_section = None
        
        if import_context.section is not None:
            
            # If this level is the at the same level, then replace the section with the current one
            if import_context.section.level <= level:
                new_section = Section()
                new_section.level = level
                new_section.super_section = import_context.section.super_section
                
            # If the current level is one higher than the new one, then move the current section under it
            elif import_context.section.level == (level + 1):
                new_section = Section()
                new_section.level = level
                new_section.super_section = import_context.section
                
            else:
                logger.warning("Did not make section for level %i in %s" %(level, self.work.title) )
                
        # Make the section 
        else:
            new_section = Section()
            new_section.level = level
            
        # Save the newly created section
        if new_section is not None:
            new_section.type = section_type
            new_section.title = title
            new_section.original_title = original_title
            new_section.save()
        
        # Set the created section as the new one
        import_context.section = new_section
        return new_section
    
    def make_chapter(self, save=True, import_context=None, descriptor="", **kwargs):
        """
        This method overrides the TextImporter.make_chapter and adds a call to save the original content section
        if necessary.
        
        Arguments:
        save -- Indicates if the content ought to be saved (or whether the save should be deferred)
        import_context -- The context being used for the process of importing.
        """
        
        # Save the XML content for the previous chapter
        self.save_original_content(import_context)
        
        import_context.chapter = TextImporter.make_chapter(self, import_context.chapter, save)
        import_context.chapter.descriptor = descriptor
        import_context.chapters.append(import_context.chapter)
        import_context.initialize_xml_doc(PerseusTextImporter.CHAPTER_TAG_NAME)
        
        # Add the chapter to the section
        if import_context.section is not None:
            import_context.section.chapters.add(import_context.chapter)
        
        return import_context.chapter
    
    def make_verse(self, import_context=None, save=True, **kwargs):
        """
        This method overrides the TextImporter.make_verse and adds a call to save the original content section
        if necessary.
        
        Arguments:
        save -- Indicates if the content ought to be saved (or whether the save should be deferred)
        import_context -- The context being used for the process of importing.
        """
        
        # Save the XML content for the previous verse
        self.save_original_verse_content(import_context)
        
        import_context.verse = TextImporter.make_verse(self, import_context.verse, import_context.chapter, save)
        import_context.initialize_xml_doc(PerseusTextImporter.VERSE_TAG_NAME)
        
        return import_context.verse
    
    def save_original_content(self, import_context):
        """
        This function takes the content from the XML node, converts it to a string and saves it in the current
        chapter as the original content.
        
        Arguments:
        import_context -- The import context being used to import the document
        """
        
        if import_context is not None and import_context.chapter is not None and import_context.document is not None:
            import_context.chapter.original_content = import_context.document.toxml()
            import_context.chapter.save()
            
    def save_original_verse_content(self, import_context):
        """
        This function takes the content from the XML node, converts it to a string and saves it in the current
        verse as the original content.
        
        Arguments:
        import_context -- The import context being used to import the document
        """
        
        if import_context is not None and import_context.verse is not None and import_context.document is not None:
            import_context.verse.original_content = import_context.document.toxml()
            import_context.verse.save()
                
        
    @staticmethod
    def getStates( refs_decl ):
        """
        Get the set of state descriptors from the given refsDecl node.
        
        Arguments:
        refs_decl -- A refsDecl node.
        """
        
        states = []
        
        state_nodes = refs_decl.getElementsByTagName("state")
        
        for state_node in state_nodes:
            states.append( State.createFromStateNode(state_node) )

        return states
        
    @staticmethod
    def getStateSets( doc, merge_all=False ):
        """
        Get the names of types of sections used in the document.
        
        Arguments:
        doc -- A minidom document representing a TEI XML file
        merge_all -- Use all state sets as if they are a single state set
        """
        
        encoding_node = doc.getElementsByTagName("encodingDesc")[0]
        
        if merge_all:
            return PerseusTextImporter.getStates(encoding_node)
            
        else:
            refs = encoding_node.getElementsByTagName("refsDecl")
            
            state_sets = []
            
            for ref in refs:
                state_sets.append( PerseusTextImporter.getStates(ref) )
                
            return state_sets
    
    @staticmethod
    def getText(nodelist, recurse=False):
        """
        Get the text node from the provided nodelist.
        
        Arguments:
        nodelist -- A list of nodes that contain at least one text-node.
        recurse -- Indicates if this function ought to get the text from the sub-nodes
        """
        
        rc = []
        
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
            elif recurse:
                rc.append( PerseusTextImporter.getText(node.childNodes, True) )
        
        return ''.join(rc)
    
    @staticmethod
    def get_language(doc):
        """
        Get the language from the language node.
        
        Arguments:
        doc -- An XML document containing a language node
        """
        
        lang_node = doc.getElementsByTagName("language")[0]
        
        language = PerseusTextImporter.getText(lang_node.childNodes).strip()
        
        return language
    
    @staticmethod
    def get_author_from_bibl_struct(bibl_struct):
        """
        Get the author from the bibleStruct node.
        
        Arguments:
        bibl_struct -- A 'biblStruct' node
        """
        
        author_node = bibl_struct.getElementsByTagName("author")[0]
        return PerseusTextImporter.getText(author_node.childNodes)
    
    @staticmethod
    def get_title_from_bibl_struct(bibl_struct):
        """
        Get the title of the text from the bibleStruct node.
        
        Arguments:
        bibl_struct -- A 'biblStruct' node
        """
        
        title_node = bibl_struct.getElementsByTagName("title")[0]
        return PerseusTextImporter.getText(title_node.childNodes)
        
    @staticmethod
    def get_title_from_tei_header(tei_header_node):
        """
        Get the title from the TEI header node.
        
        Arguments:
        tei_header_node -- A node representing the TEI header
        """
        
        for node in tei_header_node.getElementsByTagName("title"):
            if "type" in node.attributes.keys() and node.attributes["type"].value != "sub":
                return PerseusTextImporter.getText(node.childNodes)
            else:
                return PerseusTextImporter.getText(node.childNodes)
        
    
    def import_info_from_bibl_struct(self, bibl_struct_node):
        """
        Import the author and title from the bibleStruct node.
        
        Arguments:
        bibl_struct_node -- An XML document containing a 'biblStruct' node
        """
        
        # Get the title
        title = PerseusTextImporter.get_title_from_bibl_struct(bibl_struct_node)
        self.work.title = title
        self.work.save()
        
        # Get the author
        author_name = PerseusTextImporter.get_author_from_bibl_struct(bibl_struct_node)
        author = self.make_author(author_name)
        self.work.authors.add(author)
    
    def is_milestone_in_state_set(self, state_set, milestone_node):
        """
        Determines if the given milestone is for the given state set.
        
        Arguments:
        state_set -- The current set of states used to break up the text (from the header indicating the various chunking strategies)
        milestone_node -- The XML node representing the milestone
        """
        
        if self.get_state_for_milestone(state_set, milestone_node) is not None:
            return True
        else:
            return False
    
    def get_state_for_milestone(self, state_set, milestone_node):
        """
        Get the state associated with the milestone.
        
        Arguments:
        state_set -- The current set of states used to break up the text (from the header indicating the various chunking strategies)
        milestone_node -- The XML node representing the milestone
        """
        
        milestone_name = milestone_node.attributes["unit"].value
        
        for state in state_set:
            
            if state.name == milestone_name:
                return state
            
    def is_milestone_chunk(self, state_set, milestone_node):
        """
        Returns a boolean indicating if this milestone is a section (like a chapter).
        
        Arguments:
        state_set -- The current set of states used to break up the text (from the header indicating the various chunking strategies)
        milestone_node -- The XML node representing the milestone
        """
        
        state = self.get_state_for_milestone(state_set, milestone_node)
        
        if state is not None:
            return state.is_chunk()
        else:
            return False
    
    @transaction.commit_on_success
    def import_xml_document(self, document, state_set=0):
        """
        Import the given TEI document into the database.
        
        Arguments:
        document -- A parsed TEI XML document
        state_set -- The state set to use for splitting the verses.
        """
        
        # Obtain references to the nodes that contain meta-data about the book
        tei_header = document.getElementsByTagName("teiHeader")[0]
        bibl_struct_node = tei_header.getElementsByTagName("biblStruct")[0]
        
        # Get the title
        self.work.title = PerseusTextImporter.get_title_from_tei_header(tei_header)
        
        # Get the language
        self.work.language = PerseusTextImporter.get_language(tei_header)
        self.work.save()
        
        # Get the author
        author_name = PerseusTextImporter.get_author_from_bibl_struct(bibl_struct_node)
        author = self.make_author(author_name)
        self.work.authors.add(author)
        
        # Get the sectioning information
        if state_set is None or state_set == "*":
            current_state_set = PerseusTextImporter.getStateSets(document, merge_all=True)
        else:
            state_sets = PerseusTextImporter.getStateSets(document)
            current_state_set = state_sets[state_set]
        
        #Save save the information about where we got the work from
        if self.work_source is not None:
            self.work_source.work = self.work
            self.work_source.save()
            
        # Import the text
        body_node = document.getElementsByTagName("body")[0]
        
        # Chunk the text into chapters
        chapters = self.import_body_sub_node(body_node, current_state_set)
        
        # Make the verses
        logger.info("Successfully imported %i chapters of %s" % (len(chapters), self.work.title)) 
        verses_created = self.make_verses(chapters, current_state_set)
        
        logger.info("Successfully imported %i verses of %s" % (verses_created, self.work.title)) 
        
        return self.work
        
    def make_verses(self, chapters, state_set):
        """
        Parse out the verses from the chapters provided and create the individual verses.
        
        Arguments:
        chapters -- A list of chapters with the original content to get the verses from.
        state_set -- The state set to use for splitting the verses.
        """
        
        verses_created = 0
        
        for chapter in chapters:
            verses_created = verses_created + self.make_verses_for_chapter(chapter, state_set)
            
        return verses_created

    def make_verses_for_chapter(self, chapter, state_set):
        """
        Parse out the verses from the chapter content and create the individual verses.
        
        Arguments:
        chapter -- The chapter with the original content to get the verses from.
        state_set -- The state set to use for splitting the verses.
        """
        
        # Parse the XML
        chapter_doc = parseString(chapter.original_content)
        
        root_node = chapter_doc.getElementsByTagName(PerseusTextImporter.CHAPTER_TAG_NAME)[0]
        
        return self.import_verse_content( chapter, root_node, state_set)
        
    def process_original_verse_content(self, original_content, persist_nodes_as_spans=False):
        """
        Takes the original content from the verse (presumed to be from a TEI document from Perseus returns the actual verse content
        with the expected format.
        
        Arguments:
        original_content -- A verse model instance (if none, then
        """
        
        verse_doc = parseString(original_content)
        
        content_node = verse_doc.getElementsByTagName(PerseusTextImporter.VERSE_TAG_NAME)
        
        resulting_content = ""
        
        for node in content_node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                resulting_content = resulting_content + self.process_text(node.data)
                
        return resulting_content
        
        
    def import_verse_content(self, chapter, content_node, state_set, import_context = None, parent_node = None, recurse = True):
        
        # Setup an import context if this is the first, top level call
        if import_context is None:
            import_context = PerseusTextImporter.ImportContext(PerseusTextImporter.VERSE_TAG_NAME)
            import_context.chapter = chapter
            is_top_level_call = True
        else:
            is_top_level_call = False
        
        # Keep track of how many verses have been imported
        verses_created = 0
        
        # By default, we will attach content to the parent node.
        next_level_node = parent_node
        
        # This node will be populated if we create a new verse. This is necessary so that we tell upstream importers to assign content to this node.
        new_verse_node = None
        
        for node in content_node.childNodes:
            
            is_new_verse_node = False
            
            if node.nodeType == node.TEXT_NODE:
                
                # We need to see a milestone before we can set the text for a verse
                if len(node.data.strip()) > 0:
                    
                    if import_context.verse is None:
                        import_context.verse = self.make_verse(import_context, save=False)
                        verses_created = verses_created + 1
                    
                        #import_context.verse = self.make_verse(save=False, chapter=chapter)
                        logger.debug("Making new verse (since we have content for a verse but no verse itself) for chapter %s of %s" % ( str(chapter.sequence_number), self.work.title))
                    
                    import_context.verse.content = import_context.verse.content + self.process_text(node.data)
                    import_context.verse.chapter = chapter
                    import_context.verse.save()
                    
            # Is a verse marker?
            elif node.tagName == "milestone" and self.is_milestone_in_state_set(state_set, node):
                
                #self.save_original_verse_content(import_context)
                
                # Make the verse
                import_context.verse = self.make_verse(import_context, save=False)
                import_context.verse.indicator = node.attributes["n"].value
                import_context.verse.save()
                
                is_new_verse_node = True
                verses_created = verses_created + 1
                
                # Start adding the content to the new verse
                new_verse_node = import_context.current_node
                parent_node = new_verse_node
                next_level_node = new_verse_node
                
                logger.debug("Making verse %s in chapter %s of %s" % (node.attributes["n"].value, str(import_context.chapter.sequence_number), self.work.title) )
                
            # Attach the content to the chapter if it is for the current verse
            if not is_new_verse_node:
                next_level_node = import_context.append_xml(node, parent_node)
                
            # Recurse on the child-nodes
            if recurse:
                verses_created_temp, created_verse_node = self.import_verse_content(chapter, node, state_set, import_context, next_level_node, True)
                verses_created = verses_created_temp
                
                if created_verse_node is not None:
                    new_verse_node = created_verse_node # Let's save this save so that we pass it up the upstream calls
                    parent_node = new_verse_node
                    next_level_node = new_verse_node
                
        if is_top_level_call:
            self.save_original_verse_content(import_context)
            return verses_created     
        else:
            return verses_created, new_verse_node
        
    def process_text(self, text):
        """
        Convert the text if necessary. This is useful for texts that are provided in
        formats like Greek texts which are presented in beta-code format.
        
        Arguments:
        text -- The content from the XML text node
        """
        
        # Convert Greek beta code
        if self.work is not None and self.work.language == "Greek":
            text_unicode = Greek.beta_code_to_unicode(text)
            
            return text_unicode.encode('utf-8')
        
        # By default, just return the text
        else:
            return text
        
    def getSectionTitle(self, div_node):
        """
        Get the the title of a section from the head node if it exists.
        
        Arguments:
        div_node -- A div node
        """
        
        head = div_node.getElementsByTagName("head")
        
        if len(head) > 0:
            head = head[0]
            
            return self.getText(head.childNodes, True)
        
        
    def import_body_sub_node(self, content_node, state_set, import_context=None, recurse=True, parent_node=None):
        """
        Imports the content from the children of the given node (which ought to be in the body).
        
        Arguments:
        content_node -- The XML node containing the content; needs to be the body node or one of its the sub-nodes
        state_set -- A set of units that ought to be used to create the chapters and verse divisions.
        import_context -- An ImportContext instance; used for determining which book, chapter, and verse is being imported
        recurse -- Indicates if the sub-nodes of the given
        """
        
        # Setup an import context if this is the first, top level call
        if import_context is None:
            import_context = PerseusTextImporter.ImportContext(PerseusTextImporter.CHAPTER_TAG_NAME)
            is_top_level_call = True
        else:
            is_top_level_call = False
        
        # By default, we will attach content to the parent node.
        next_level_node = parent_node
        
        # This node will be populated if we create a new chapter. This is necessary so that we tell upstream importers to assign content to this node.
        new_chapter_node = None
        
        # Let's go through each node and pull in the content until we find the next chapter marker
        for node in content_node.childNodes:
            
            # We have to handle several nodes here:
            #    * milestone: if a chapter divider, then split accordingly
            #    * div1: indicates a new book, make a section accordingly
            #    * everything else: add it to the current chapter XML content
            
            # Determine if the node is a chapter marker
            is_new_chapter_marker = not node.nodeType == node.TEXT_NODE and node.tagName == "milestone" and self.is_milestone_chunk(state_set, node)
            
            # If the content is a text-node, then attach it the current chapter
            if node.nodeType == node.TEXT_NODE:
                
                if import_context.chapter is None:
                    # No chapter exists yet, skipping this verse
                    logger.debug("No chapter exists yet, skipping this content: %s of %s" % (node.data, self.work.title))
                    
            # If the content is a new chapter marker
            elif is_new_chapter_marker:
                
                descriptor = ""
                
                if 'n' in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                
                # Make the chapter
                self.make_chapter(import_context=import_context, descriptor=descriptor)
                logger.debug("Making chapter %s (since it is a chunk) of %s" % ( str(import_context.chapter.sequence_number), self.work.title))
                
                # Start adding the content to the new chapter
                new_chapter_node = import_context.current_node
                parent_node = new_chapter_node
                next_level_node = new_chapter_node
                
            # If the content is a verse marker and we don't have a chapter, then create one
            elif node.tagName == "milestone" and self.is_milestone_in_state_set(state_set, node):
                
                descriptor = ""
                
                if 'n' in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                
                # If we have a verse without a chapter, then go ahead and make one
                if import_context.chapter is None:
                    self.make_chapter(import_context=import_context, descriptor=descriptor)
                    new_chapter_node = import_context.current_node
                    parent_node = new_chapter_node
                    next_level_node = new_chapter_node
                    
                    # We just below away the existing chapter is carry the content over
                    
                    logger.debug("Making a chapter for %s since once does not exist yet (so that we can add a verse)" % (self.work.title))
            
            elif PerseusTextImporter.DIV_PARSE_REGEX.match( node.tagName):
                
                # Get the level from the tag name
                m = PerseusTextImporter.DIV_PARSE_REGEX.search( node.tagName )
                level = int(m.groupdict()['level'] )
                
                # Get the type of the section
                section_type = None
                
                if "type" in node.attributes.keys():
                    section_type = node.attributes["type"].value
                
                original_title = self.getSectionTitle(node)
                title = self.process_text(original_title)
                
                self.make_section(level, import_context, section_type, title=title, original_title=original_title)
                
                logger.debug("Making section at level %i in %s" % (level, self.work.title))
                
            #elif node.tagName == "note":
                # We don't yet handle these types of nodes so don't try to get the text under them
                #recurse = False
                
            # Attach the content to the chapter if it is for the current chapter
            if not is_new_chapter_marker:
                next_level_node = import_context.append_xml(node, parent_node)
                
            # Recurse on the child-nodes
            if recurse:
                created_chapter_node = self.import_body_sub_node(node, state_set, import_context, True, parent_node=next_level_node)
                
                if created_chapter_node is not None:
                    new_chapter_node = created_chapter_node # Let's save this save so that we pass it up the upstream calls
                    parent_node = new_chapter_node
                    next_level_node = new_chapter_node
                    
        # We may have content left for the final chapter. Go ahead and persist it.
        if is_top_level_call:
            self.save_original_content(import_context)
            return import_context.chapters
            
        return new_chapter_node