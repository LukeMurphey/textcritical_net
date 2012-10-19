'''
Created on Sep 2, 2012

@author: Luke

The Perseus importer takes content from the TEI XML files and moves the content into the database.

The importer performs the import in the three major steps:

 1) Split up the text into the logical divisions
 2) Create the verses
 3) Process the verses (convert original content to something that can be displayed)
'''

from xml.dom import minidom
from xml.dom.minidom import parse, parseString
import logging
import re

from reader.importer import TextImporter
from reader.models import Division, Work
from reader.shortcuts import transform_text

from django.db import transaction
from django.template.defaultfilters import slugify

# Get an instance of a logger
logger = logging.getLogger(__name__)

class State():
    
    def __init__(self, name, section_type, level):
        self.section_type = section_type
        self.name = name
        self.level = level
        
    def is_chunk(self):
        return self.section_type is not None
        
    @staticmethod
    def createFromStateNode( state_node, level = None ):
        
        unit_name = state_node.attributes["unit"].value
            
        if state_node.attributes.get("n", None) != None:
            section_type = state_node.attributes["n"].value
        else:
            section_type = None
            
        return State(unit_name, section_type, level)
    
    def __str__(self):
        return self.name

class PerseusTextImporter(TextImporter):
    
    DIV_PARSE_REGEX = re.compile( r"div(?P<level>[0-9]+)" )
    
    VERSE_TAG_NAME = "verse"
    CHAPTER_TAG_NAME = "chapter"
    
    def __init__(self, overwrite_existing=False, state_set=0, work=None, work_source=None):
        self.overwrite_existing = overwrite_existing
        
        self.state_set = state_set
        
        if state_set != "*":
            self.state_set = int(self.state_set)
        
        TextImporter.__init__(self, work, work_source)
        #super(PerseusTextImporter, self).__init__(work, work_source)
    
    def import_xml_string(self, xml_string ):
        """
        Import the work from the string provided.
        
        Arguments:
        xml_string -- A string representing XML
        state_set -- The state set to use
        """
        
        doc = parseString(xml_string)
        return self.import_xml_document(doc)
         
    def import_file( self, file_name):
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
        return self.import_xml_document(doc)
    
    def make_division(self, import_context, level=1, sequence_number=None, division_type=None, title=None, original_title=None, descriptor=None, state_info=None):
        
        if state_info is not None:
            level = state_info.level
        
        # Save the XML content for the previous chapter
        self.save_original_content(import_context)
        
        import_context.initialize_xml_doc(PerseusTextImporter.CHAPTER_TAG_NAME)
        
        new_division = Division()
        new_division.level = level
        
        if import_context.division is not None:
            
            # Populate the sequence number from the previous division is available
            if sequence_number is None:
                sequence_number = import_context.division.sequence_number + 1
            
            # If this level is the at the same level as the current one, then replace the division with the current one
            if level == import_context.division.level:
                new_division.parent_division = import_context.division.parent_division
                
            # If the new level is lower than the current one, then shim in the new one at the appropriate level
            elif level <= import_context.division.level:
                
                same_level_division = import_context.division
                
                # Move down the levels until we find one at the same level
                while same_level_division is not None and level < same_level_division.level:
                    same_level_division = same_level_division.parent_division
                
                if same_level_division is not None:
                    new_division.parent_division = same_level_division.parent_division
                else:
                    logger.warn( "Unable to find parent division for level %i" % (level) )
            
            # If the new level is higher than the current one, then add
            else:
                new_division.parent_division = import_context.division
                
            #else:
            #    logger.warning("Did not make division for level %i in %s" %(level, self.work.title) )
                
        # Make the section 
        else:
            
            # Start the sequence number at 1 if a number was not provided
            if sequence_number is None:
                sequence_number = 1
            
        if descriptor is None:
            descriptor = sequence_number
            
        # Save the newly created section
        if new_division is not None:
            
            new_division.type = division_type
            new_division.title = title
            
            if title is not None:
                new_division.descriptor = slugify(title)
            else:
                new_division.descriptor = descriptor
            
            new_division.original_title = original_title
            new_division.work = self.work
            new_division.sequence_number = sequence_number
            
            if state_info is not None:
                new_division.level = state_info.level
                new_division.type = state_info.name
                new_division.readable_unit = state_info.is_chunk()
            
            new_division.save()
        
        logger.debug( "Successfully created division: %s %s" % (new_division.descriptor, new_division.original_title) )
        
        # Set the created division as the new one
        import_context.divisions.append(new_division)
        import_context.division = new_division
        return new_division
    
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
        
        if import_context.verse is not None:
            import_context.initialize_xml_doc()
        
        import_context.verse = TextImporter.make_verse(self, import_context.verse, import_context.division, save)
        
        return import_context.verse
    
    def save_original_content(self, import_context):
        """
        This function takes the content from the XML node, converts it to a string and saves it in the current
        division as the original content.
        
        Arguments:
        import_context -- The import context being used to import the document
        """
        
        if import_context is not None and import_context.division is not None and import_context.document is not None:
            import_context.division.original_content = import_context.document.toxml()
            import_context.division.save()
        else:
            logger.error("Cannot save division content")
        
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
        else:
            logger.error("Cannot save verse content %r" % (import_context.verse))
        
    @staticmethod
    def getStates( refs_decl ):
        """
        Get the set of state descriptors from the given refsDecl node.
        
        Arguments:
        refs_decl -- A refsDecl node.
        """
        
        states = []
        
        state_nodes = refs_decl.getElementsByTagName("state")
        i = 1
        
        for state_node in state_nodes:
            states.append( State.createFromStateNode(state_node, i) )
            i = i + 1

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
        
        lang_nodes = doc.getElementsByTagName("language")
        
        if len(lang_nodes) > 0:
            return PerseusTextImporter.getText(lang_nodes[0].childNodes).strip()
        else:
            return None
    
    @staticmethod
    def get_author_from_bibl_struct(bibl_struct):
        """
        Get the author from the bibleStruct node.
        
        Arguments:
        bibl_struct -- A 'biblStruct' node
        """
        
        author_nodes = bibl_struct.getElementsByTagName("author")
        
        if len(author_nodes) > 0:
            return PerseusTextImporter.getText(author_nodes[0].childNodes)
        else:
            return None
    
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
    
    def delete_equivalent_works(self):
        """
        Deletes works that are equivalent to the one we are importing or have imported.
        """
        
        equivalent_works = Work.objects.exclude(id=self.work.id).filter( title=self.work.title, language=self.work.language, authors=self.work.authors.all() )
        
        for work in equivalent_works:
            logger.info("Deleting work so that new copy can replace it, title=%s, work.id=%i", work.title, work.id)
            work.delete()
    
    @transaction.commit_on_success
    def import_xml_document(self, document):
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
        title = PerseusTextImporter.get_title_from_tei_header(tei_header)
        
        if self.work is None:
            self.make_work(title)
        else:
            self.work.title = title
        
        # Get the language
        self.work.language = PerseusTextImporter.get_language(tei_header)
        self.work.save()
        
        # Get the author
        author_name = PerseusTextImporter.get_author_from_bibl_struct(bibl_struct_node)
        author = self.make_author(author_name)
        self.work.authors.add(author)
          
        # Delete pre-existing works if they exist
        if self.overwrite_existing:
            self.delete_equivalent_works()
        
        # Get the sectioning information
        if self.state_set is None or self.state_set == "*":
            current_state_set = PerseusTextImporter.getStateSets(document, merge_all=True)
        else:
            state_sets = PerseusTextImporter.getStateSets(document)
            current_state_set = state_sets[self.state_set]
        
        #Save save the information about where we got the work from
        if self.work_source is not None:
            self.work_source.work = self.work
            self.work_source.save()
            
        # Import the text
        body_node = document.getElementsByTagName("body")[0]
        
        # Chunk the text into divisions
        divisions = self.import_body_sub_node(body_node, current_state_set)
        
        # Make the verses
        logger.info("Successfully imported %i divisions of %s" % (len(divisions), self.work.title)) 
        verses_created = self.make_verses(divisions, current_state_set)
        
        logger.info("Successfully imported %i verses of %s" % (verses_created, self.work.title)) 
        
        return self.work
        
    def make_verses(self, divisions, state_set):
        """
        Parse out the verses from the divisions provided and create the individual verses.
        
        Arguments:
        divisions -- A list of divisions with the original content to get the verses from.
        state_set -- The state set to use for splitting the verses.
        """
        
        verses_created = 0
        
        for division in divisions:
            verses_created = verses_created + self.make_verses_for_division(division, state_set)
        
        return verses_created

    def make_verses_for_division(self, division, state_set):
        """
        Parse out the verses from the division content and create the individual verses.
        
        Arguments:
        division -- The division with the original content to get the verses from.
        state_set -- The state set to use for splitting the verses.
        """
        
        # Parse the original content if it is available
        if division.original_content:
            
            division_doc = parseString(division.original_content)
            
            root_node = division_doc.getElementsByTagName(PerseusTextImporter.CHAPTER_TAG_NAME)[0]
            
            return self.import_verse_content( division, root_node, state_set)
        
        else:
            return 0
    
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
        
        
    def import_verse_content(self, division, content_node, state_set, import_context = None, parent_node = None, recurse = True):
        
        # Setup an import context if this is the first, top level call
        if import_context is None:
            import_context = PerseusTextImporter.ImportContext(PerseusTextImporter.VERSE_TAG_NAME)
            import_context.division = division
            is_top_level_call = True
        
        else:
            is_top_level_call = False
        
        # Keep track of how many verses have been imported
        verses_created = 0
        
        # By default, we will attach content to the parent node.
        next_level_node = parent_node
        
        # This node will be populated if we create a new verse. This is necessary so that we tell upstream importers to assign content to this node.
        new_verse_node = None
        
        # Process each node
        for node in content_node.childNodes:
            
            # This determines if the content is ought to be attached to a verse
            attach_xml_content = True
            
            if node.nodeType == node.TEXT_NODE:
                
                # We need to see a milestone before we can set the text for a verse
                
                if len(node.data.strip()) > 0:
                    
                    # Start importing the verse if we got a division start but not a verse marker (which is possible)
                    if import_context.verse is None and import_context.division is not None:
                        self.make_verse(import_context, save=False)
                        
                        # Start adding the content to the new verse
                        new_verse_node = import_context.current_node
                        parent_node = new_verse_node
                        next_level_node = new_verse_node
                        
                        verses_created = verses_created + 1
                    
                        #import_context.verse = self.make_verse(save=False, division=division)
                        logger.debug("Making new verse (since we have content for a verse but no verse itself) for division %s of %s" % ( str(division.sequence_number), self.work.title))
                    
                    if import_context.verse is not None:
                        import_context.verse.content = import_context.verse.content + self.process_text(node.data)
                        import_context.verse.save()
                    else:
                        attach_xml_content = False
                
                #elif import_context.verse is None:
                #    attach_xml_content = False
                
            # Is a verse marker?
            elif node.tagName == "milestone" and self.is_milestone_in_state_set(state_set, node):
                
                # Make the verse
                self.make_verse(import_context, save=False)
                import_context.verse.indicator = node.attributes["n"].value
                import_context.verse.save()
                
                attach_xml_content = False
                verses_created = verses_created + 1
                
                # Start adding the content to the new verse
                new_verse_node = import_context.current_node
                parent_node = new_verse_node
                next_level_node = new_verse_node
                
                logger.debug("Making verse %s in division %s of %s" % (node.attributes["n"].value, str(import_context.division.sequence_number), self.work.title) )
                
            elif node.tagName in ["milestone"]:
                # Don't include:
                #  1) milestone nodes that are not in the current state set in the XML
                attach_xml_content = True
                
            elif node.tagName == "list" and "type" in node.attributes.keys() and node.attributes["type"].value == "toc":
                logger.critical("Skipping attachment of a list ")
                attach_xml_content =  False
                recurse = False
                
            elif node.tagName == "note" and "type" in node.attributes.keys() and node.attributes["type"].value == "title":
                logger.critical("Skipping attachment of the title node")
                attach_xml_content =  False
                recurse = False
                
            elif node.tagName in ["head"]:
                # Don't include: 
                #  1) head tag since we already pulled this in when we got the division tag
                #  2) notes since we don't handle them yet
                attach_xml_content =  False
                recurse = False
                
            elif node.tagName.startswith("div"):
                attach_xml_content =  False
                
            # Attach the content to the division if it is for the current verse
            if attach_xml_content:
                next_level_node = import_context.append_xml(node, parent_node)
                
            # Recurse on the child-nodes
            if recurse:
                verses_created_temp, created_verse_node = self.import_verse_content(division, node, state_set, import_context, parent_node=next_level_node, recurse=True)
                verses_created = verses_created + verses_created_temp
                
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
        if self.work is not None:
            return transform_text(text, self.work.language)
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
        state_set -- A set of units that ought to be used to create the divisions and verse divisions.
        import_context -- An ImportContext instance; used for determining which book, division, and verse is being imported
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
        
        # This node will be populated if we create a new division. This is necessary so that we tell upstream importers to assign content to this node.
        new_division_node = None
        
        # Let's go through each node and pull in the content until we find the next division marker
        for node in content_node.childNodes:
            
            # Determines if we are going to merge the XML content to the original content for the given section
            append_xml_content = True
            
            # We have to handle several nodes here:
            #    * milestone: if a division divider, then split accordingly
            #    * div1: indicates a new book, make a section accordingly
            #    * everything else: add it to the current division XML content
            
            # If the content is a text-node, then attach it the current division
            if node.nodeType == node.TEXT_NODE:
                
                if import_context.division is None:
                    # No division exists yet, skipping this verse
                    logger.debug("No division exists yet, skipping this content: %s of %s" % (node.data, self.work.title))
            
            elif node.nodeType == minidom.Node.COMMENT_NODE:
                append_xml_content = False # Skip comments
            
            # If the content is a new milestone marker
            elif node.tagName == "milestone" and self.is_milestone_chunk(state_set, node):
                
                append_xml_content = False
                
                descriptor = ""
                
                if 'n' in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                
                # Make the division
                self.make_division(import_context=import_context, descriptor=descriptor, state_info=self.get_state_for_milestone(state_set, node))
                logger.debug("Making division %s (since it is a chunk) of %s" % ( str(import_context.division.sequence_number), self.work.title))
                
                # Start adding the content to the new division
                new_division_node = import_context.current_node
                parent_node = new_division_node
                next_level_node = new_division_node
                
            # If the content is a verse marker and we don't have a division, then create one
            elif node.tagName == "milestone" and self.is_milestone_in_state_set(state_set, node):
                
                descriptor = ""
                
                if 'n' in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                
                # If we have a verse without a division, then go ahead and make one
                if import_context.division is None:
                    self.make_division(import_context=import_context, descriptor=descriptor, state_info=self.get_state_for_milestone(state_set, node))
                    logger.debug("Making a division for %s since once does not exist yet (so that we can add a verse)" % (self.work.title))
                    
                    # Start adding the content to the new division
                    new_division_node = import_context.current_node
                    parent_node = new_division_node
                    next_level_node = new_division_node
                
            elif PerseusTextImporter.DIV_PARSE_REGEX.match( node.tagName ):
                
                # Get the level from the tag name
                m = PerseusTextImporter.DIV_PARSE_REGEX.search( node.tagName )
                level = int(m.groupdict()['level'] )
                
                # Get the type of the section
                division_type = None
                descriptor = None
                
                if "type" in node.attributes.keys():
                    division_type = node.attributes["type"].value
                    
                if "n" in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                
                original_title = self.getSectionTitle(node)
                title = self.process_text(original_title)
                
                # Get the state set associated with this entry
                for state in state_set:
                    if state.name.lower() == division_type.lower() and state.level is not None:
                        level = state.level
                        break
                
                self.make_division(import_context, level, division_type=division_type, title=title, original_title=original_title, descriptor=descriptor)
                
                # Start adding the content to the new division
                new_division_node = import_context.current_node
                parent_node = new_division_node
                next_level_node = new_division_node
                
                logger.debug("Making division at level %i in %s" % (level, self.work.title))
                
                append_xml_content = False
            #elif node.tagName == "note":
                # We don't yet handle these types of nodes so don't try to get the text under them
                #recurse = False
                
            # Attach the content to the division if it is for the current division
            if append_xml_content:
                next_level_node = import_context.append_xml(node, parent_node)
                
            # Recurse on the child-nodes
            if recurse:
                created_division_node = self.import_body_sub_node(node, state_set, import_context, True, parent_node=next_level_node)
                
                if created_division_node is not None:
                    new_division_node = created_division_node # Let's save this save so that we pass it up the upstream calls
                    parent_node = new_division_node
                    next_level_node = new_division_node
                    
        # We may have content left for the final division. Go ahead and persist it.
        if is_top_level_call:
            self.save_original_content(import_context)
            return import_context.divisions
            
        return new_division_node