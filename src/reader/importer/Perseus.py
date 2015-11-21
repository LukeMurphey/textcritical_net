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
from xml.dom.minidom import parseString
import logging
import re

from reader.importer import TextImporter, LineNumber, LineNumberRange
from reader.models import Division, Work
from reader.shortcuts import transform_text

from django.db import transaction
from django.template.defaultfilters import slugify
import codecs

# Get an instance of a logger
logger = logging.getLogger(__name__)

class State():
    
    CHUNK_TYPES = ["card", "chapter"]
    
    def __init__(self, name, section_type, level, chunk=None):
        self.section_type = section_type
        self.name = name
        self.level = level
        self.chunk = chunk
        
    def is_chunk(self):
        if self.chunk == True:
            return True
        elif self.section_type is not None:
            return True
        elif self.name in State.CHUNK_TYPES:
            return True
        else:
            return False
        
    @staticmethod
    def createFromStateNode( state_node, level = None, chunk = None ):
        
        unit_name = state_node.attributes["unit"].value
            
        if state_node.attributes.get("n", None) != None:
            section_type = state_node.attributes["n"].value
        else:
            section_type = None
            
        return State(unit_name, section_type, level, chunk)
    
    def __str__(self):
        return self.name

class PerseusTextImporter(TextImporter):
    
    DIV_PARSE_REGEX = re.compile( r"div(?P<level>[0-9]+)" )
    
    VERSE_TAG_NAME = "verse"
    CHAPTER_TAG_NAME = "chapter"
    
    def __init__(self, overwrite_existing=False, state_set=0, work=None, work_source=None, ignore_division_markers=False, use_line_count_for_divisions=None,
                       ignore_content_before_first_milestone=False, ignore_undeclared_divs=False, only_last_state_is_non_chunk=False,
                       only_leaf_divisions_readable=False, division_tags=None):
        """
        Constructs a Perseus text importer.
        
        Arguments:
        overwrite_existing -- indicates if an existing work ought to be deleted
        state_set -- indicates which state set to use
        work -- the work to populate (one will be created otherwise)
        work_source -- the work source associated with this work
        ignore_division_markers -- if true, division markers will be ignored
        use_line_count_for_divisions -- if true, then the titles of the readable units will be the line count range
        ignore_content_before_first_milestone -- if true, then content before the first milestone will be ignored
        ignore_undeclared_divs -- if true, then divs that are not in the refsdecl will be ignored
        only_last_state_is_non_chunk -- if true, then all state in the refsdecl other than the last one will assumed to be chunks
        only_bottom_division_readable -- if true, then only the bottom-most division will be allowed to be readable
        division_tags -- if not none, only division tags within this list will be considered valid
        """
        
        self.overwrite_existing = overwrite_existing
        
        self.state_set = state_set
        
        if state_set != "*":
            self.state_set = int(self.state_set)
        
        TextImporter.__init__(self, work, work_source)
        
        self.ignore_division_markers = ignore_division_markers
        self.use_line_count_for_divisions = use_line_count_for_divisions
        self.ignore_content_before_first_milestone = ignore_content_before_first_milestone
        self.ignore_undeclared_divs = ignore_undeclared_divs
        self.only_last_state_is_non_chunk = only_last_state_is_non_chunk
        self.only_leaf_divisions_readable = only_leaf_divisions_readable
        
        if division_tags is not None:
            self.division_tags = division_tags[:]
        else:
            self.division_tags = None
    
    def import_xml_string(self, xml_string ):
        """
        Import the work from the string provided.
        
        Arguments:
        xml_string -- A string representing XML
        state_set -- The state set to use
        """
        
        doc = parseString(xml_string)
        
        try:
            return self.import_xml_document(doc)
        finally:
            doc.unlink() 
            del(doc)
         
    def import_file( self, file_name, encoding='utf-8'):
        """
        Import the provided XML file.
        
        Arguments:
        file_name -- The file name of a Perseus XML work
        encoding -- The encoding to use
        """
        
        # Create the source object so that we remember where we got the file
        #self.work_source = WorkSource()
        #self.work_source.source = "Perseus.tufts.edu"
        #self.work_source.resource = os.path.basename(file_name)
        
        # Import the document
        # Read the file into a string
        f = None
        
        try:
            f = codecs.open( file_name, 'r', encoding )

            file_string = f.read()
        finally:
            if f:
                f.close()
        
        file_string = file_string.encode('utf-8')
        doc = parseString(file_string)
        
        try:
            return self.import_xml_document(doc)
        finally:
            doc.unlink()
            del(doc)
    
    def close_division(self, import_context, new_division=None):
        """
        This function is called when a new division is found and the importer is about to move on to a new division.
        
        Arguments:
        import_context -- The import context being used during importation
        new_division -- The new division to be created
        """
        
        """
        if import_context.division is not None and self.use_line_count_for_divisions == True :
            
            if new_division and new_division.descriptor is not None and LineNumber.is_line_number(new_division.descriptor):
                next_line_number = LineNumber(new_division.descriptor)
                next_line_number.decrement()
                    
                import_context.line_number_end = next_line_number
            else:
                self.update_line_count_info(import_context, reset_start_line_count=False)
                    
            if import_context.line_number_end.number > 0:
                # Set the division title if we have a division to update
                import_context.division.title = import_context.get_line_count_title()
                    
                # Restart the line count for the next division
                import_context.reset_start_line_count()
        """
        
        # Save the XML content for the previous chapter
        self.save_original_content(import_context)
    
    def make_division(self, import_context, level=1, sequence_number=None, division_type=None, title=None, original_title=None, descriptor=None, state_info=None):
        
        # Get the level from the state info object unless the level was already provided
        if state_info is not None:
            level = state_info.level
        
        elif level is None:
            level = 1
            
        # Create the new division
        new_division = Division()
        new_division.level = level
        
        new_division.type = division_type
        new_division.title = title
        new_division.descriptor = descriptor
        new_division.original_title = original_title
        new_division.work = self.work
        
        if state_info is not None:
            new_division.type = state_info.name
        
        # Save the existing division if one exists
        if import_context.division is not None:
            
            # Populate the sequence number from the previous division is available
            if sequence_number is None:
                sequence_number = import_context.division.sequence_number + 1
            
            # If this level is the at the same level as the current one, then replace the division with the current one
            if level == import_context.division.level:
                new_division.parent_division = import_context.division.parent_division
                
            # If the new level is higher in value (i.e. lower and nearer to the bottom) than the current one, then shim in the new one at the appropriate level
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
        
        # Set the sequence number now that we got it
        new_division.sequence_number = sequence_number
        
        # Update the count of divisions observed at the given level    
        import_context.increment_division_level(level)
        
        # Assign the descriptor if one was not provided
        if descriptor is None:
            new_division.descriptor = import_context.get_division_level_count(level)
            
        # Close the existing division
        self.close_division(import_context, new_division)
        
        # Start the XML document for the new division
        import_context.initialize_xml_doc(PerseusTextImporter.CHAPTER_TAG_NAME)
            
        # Save the newly created section
        if new_division is not None:
            new_division.save()
        
        # Log the creation of a division
        if new_division.parent_division is not None:
            logger.debug( "Successfully created division: descriptor=%s, title=%s, id=%i, level=%i, parent=%s", new_division.descriptor, new_division.original_title, new_division.id, level, str(new_division.parent_division.descriptor) )
        else:
            logger.debug( "Successfully created division: descriptor=%s, title=%s, id=%i, level=%i", new_division.descriptor, new_division.original_title, new_division.id, level )
        
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
        
        # If we are only to allow edge division nodes as readable units, then make sure divisions with children are not set as readable
        if self.only_leaf_divisions_readable and import_context.division is not None and import_context.division.readable_unit == True:
            
            # If the division has children, make sure readability is set to false
            if Division.objects.filter(parent_division=import_context.division).count() > 0:
                import_context.division.readable_unit = False
                import_context.division.save()
        
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
    def getText(nodelist, recurse=False, separator=''):
        """
        Get the text node from the provided nodelist.
        
        Arguments:
        nodelist -- A list of nodes that contain at least one text-node.
        recurse -- Indicates if this function ought to get the text from the sub-nodes
        separator -- The separator to use when putting the text of the element together
        """
        
        rc = []
        
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
            elif recurse:
                rc.append( PerseusTextImporter.getText(node.childNodes, True) )
        
        return separator.join(rc)
    
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
    def get_author_from_tei_header(tei_header_node):
        """
        Get the author from the TEI header node.
        
        Arguments:
        tei_header_node -- A node representing the TEI header
        """
        
        author_nodes = tei_header_node.getElementsByTagName("author")
        
        if len(author_nodes) > 0:
            return PerseusTextImporter.getText(author_nodes[0].childNodes)
        else:
            return None
    
    @staticmethod
    def get_editors( tei_document ):
        """
        Get the editors from the TEI document.
        
        Arguments:
        tei_document -- A TEI document
        """
        
        tei_header = tei_document.getElementsByTagName("teiHeader")
        
        if len(tei_header) > 0:
            tei_header = tei_header[0]
        else:
            return
        
        # Try to get the editor from the teiHeader
        editors = []
        editor_nodes = tei_header.getElementsByTagName("editor")
        
        if len(editor_nodes) > 0:
            for ed in editor_nodes:
                
                editor = PerseusTextImporter.getText(ed.childNodes)
                
                # If the editor has an "and" in it, then split up the editor into two fields
                editors_and = editor.split("and")
                
                if len(editors_and) > 1:
                    for e in editors_and:
                        editors.append( e.strip() )
                        
                else:
                    editors.append( editor )
        else:
            return None
        
        return editors
    
    @staticmethod
    def get_author( tei_document ):
        """
        Get the author from the TEI document.
        
        Arguments:
        tei_document -- A TEI document
        """
        
        tei_header = tei_document.getElementsByTagName("teiHeader")
        bibl_struct_node = None
        
        if tei_header is not None and len(tei_header) > 0:
            bibl_struct_node = tei_header[0].getElementsByTagName("biblStruct")
        
        # Try to get the author from the biblStruct
        if bibl_struct_node is not None and len(bibl_struct_node) > 0:
            author = PerseusTextImporter.get_author_from_bibl_struct(bibl_struct_node[0])
        
            if author is not None:
                return author
        
        # Otherwise, try to get the author from the titleStmt
        if tei_header is not None and len(tei_header) > 0:
            author = PerseusTextImporter.get_author_from_tei_header(tei_header[0])
            
            return author
        
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
        return PerseusTextImporter.process_title( PerseusTextImporter.getText(title_node.childNodes) )
        
    @staticmethod
    def use_line_numbers_for_division_titles(tei_header_node):
        """
        Determines if the readable unit divisions ought to be set to the line numbers.
        
        Arguments:
        tei_header_node -- A node representing the TEI header
        """
        
        for step_node in tei_header_node.getElementsByTagName("step"):
            
            if "refunit" in step_node.attributes.keys() and step_node.attributes["refunit"].value == "line":
                return True
            else:
                return False
        
    @staticmethod
    def process_title(title):
        """
        Prepare the title by removing content that is not necessary.
        
        Arguments:
        title -- The title to be processed.
        """
        
        title = title.strip()
        
        title = title.replace("(Greek). Machine readable text", "")
        title = title.replace("(English). Machine readable text", "")
        title = title.replace("(English)", "")
        
        # Strip trailing periods
        if title.endswith("."):
            title = title[0:-1]
        
        title = title.strip()
        
        return title
        
    @staticmethod
    def get_title_from_tei_header(tei_header_node):
        """
        Get the title from the TEI header node.
        
        Arguments:
        tei_header_node -- A node representing the TEI header
        """
        
        for node in tei_header_node.getElementsByTagName("title"):
            if "type" in node.attributes.keys() and node.attributes["type"].value != "sub":
                return PerseusTextImporter.process_title( PerseusTextImporter.getText(node.childNodes, recurse=True) )
            elif "type" in node.attributes.keys() and node.attributes["type"].value == "sub":
                pass # Don't include sub-titles
            else:
                return PerseusTextImporter.process_title( PerseusTextImporter.getText(node.childNodes, recurse=True) )
        
    
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
        
        # Add the author only if not blank
        if author_name is not None and len(author_name) > 0:
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
            
    def is_milestone_chunk(self, state_set, milestone_node, only_last_state_is_non_chunk=False):
        """
        Returns a boolean indicating if this milestone is a section (like a chapter).
        
        Arguments:
        state_set -- The current set of states used to break up the text (from the header indicating the various chunking strategies)
        milestone_node -- The XML node representing the milestone
        only_last_state_is_non_chunk -- Only allow the last state to be a non-chunk; all others will be considered chunks
        """
        
        # Determine if this is one of the nodes we always treat as a chunk
        if milestone_node.attributes["unit"].value in State.CHUNK_TYPES:
            return True
        
        state = self.get_state_for_milestone(state_set, milestone_node)
        
        # If the state is not the last one, then treat it as a chunk
        if state is not None and only_last_state_is_non_chunk and state.name != state_set[-1].name:
            return True
        
        if state is not None:
            return state.is_chunk()
        else:
            return False
    
    def delete_equivalent_works(self, title=None, language=None):
        """
        Deletes works that are equivalent to the one we are importing or have imported.
        """
        
        if self.work.id is not None:
            equivalent_works = Work.objects.exclude(id=self.work.id).filter( title=self.work.title, language=self.work.language) #, authors=self.work.authors.all() )
        else:
            equivalent_works = Work.objects.filter( title=self.work.title, language=self.work.language) #, authors=self.work.authors.all() )
        
        for work in equivalent_works:
            logger.info("Deleting work so that new copy can replace it, title=%s, work.id=%i", work.title, work.id)
            work.delete()
    
    @transaction.atomic
    def import_xml_document(self, document):
        """
        Import the given TEI document into the database.
        
        Arguments:
        document -- A parsed TEI XML document
        """            
        
        # Obtain references to the nodes that contain meta-data about the book
        tei_header = document.getElementsByTagName("teiHeader")[0]
        
        # Get the title
        title = PerseusTextImporter.get_title_from_tei_header(tei_header)
        
        if self.work is None:
            self.make_work(title)
        else:
            self.work.title = title
        
        # Get the language
        language = PerseusTextImporter.get_language(tei_header)
        self.work.language = language
        
        # Delete pre-existing works if they exist
        if self.overwrite_existing:
            self.delete_equivalent_works(title=title, language=language)
        
        # Save the work
        self.work.save()
        
        # Determine if the division titles should be set to the line numbers
        if self.use_line_count_for_divisions is None:
            self.use_line_count_for_divisions = PerseusTextImporter.use_line_numbers_for_division_titles(tei_header)
        
        # Get the editors
        editor_names = PerseusTextImporter.get_editors(document)
        
        # Add the editors only if we got some
        if editor_names is not None:
            
            for editor_name in editor_names:
                editor = self.make_author(editor_name)
                self.work.editors.add(editor)
        
        # Get the author
        author_name = PerseusTextImporter.get_author(document)
        
        # Add the author only if not blank
        if author_name is not None and len(author_name) > 0:
            author = self.make_author(author_name)
            self.work.authors.add(author)
        
        # Get the sectioning information
        if self.state_set is None or self.state_set == "*":
            current_state_set = PerseusTextImporter.getStateSets(document, merge_all=True)
        else:
            state_sets = PerseusTextImporter.getStateSets(document)
            current_state_set = state_sets[self.state_set]
        
        # Save the information about where we got the work from
        if self.work_source is not None:
            self.work_source.work = self.work
            self.work_source.save()
        
        # Look for group nodes which indicate the presence of multiple text nodes (from which we will start the import)
        body_node = document.getElementsByTagName("group")
        
        # If no group nodes exist, then just import starting at the body node
        if body_node is not None and len(body_node) > 0:
            body_node = body_node[0]
        else:
            body_node = document.getElementsByTagName("body")[0]  
        
        # Chunk the text into divisions
        divisions = self.import_body_sub_node(body_node, current_state_set)
        
        if len(divisions) == 0:
            self.work.delete() # Delete the work just in case the transaction doesn't get rolled back 
            raise Exception("No divisions were discovered, title=%s" % (self.work.title) )
        else:
            logger.info("Successfully imported divisions of work, division_count=%i, title=%s", len(divisions), self.work.title)
            
        # Make the verses
        verses_created = self.make_verses(divisions, current_state_set)
        
        if verses_created == 0:
            self.work.delete() # Delete the work just in case the transaction doesn't get rolled back
            raise Exception("No verses were discovered, title=%s" % (self.work.title) )
        else:
            logger.info("Successfully imported verse of work, verse_count=%i, title=%s", verses_created, self.work.title) 
        
        return self.work
        
    def make_verses(self, divisions, state_set):
        """
        Parse out the verses from the divisions provided and create the individual verses.
        
        Arguments:
        divisions -- A list of divisions with the original content to get the verses from.
        state_set -- The state set to use for splitting the verses.
        """
        
        verses_created = 0
        line_number_range = LineNumberRange()
        previous_line_number_division = None
        previous_line_number_range = None
        
        for division in divisions:
            
            # Make the verse
            verses_created = verses_created + self.make_verses_for_division(division, state_set)
            
            # The following is for setting the titles of divisions which ought to indicate the line numbers
            
            # Set the line count if necessary (but only if the division is a leaf node)
            if self.use_line_count_for_divisions == True and Division.objects.filter(parent_division=division).count() == 0:# and verses_created > 0:
                
                # Parse the content
                original_content = division.original_content.encode('utf-8')
                division_doc = parseString(original_content)
                
                # Update the line count by looking through the verse nodes and counting the relevant tags or looking for verse nodes that include a count
                line_number_range = self.update_line_count_info(division_doc, line_number_range, reset_start_line_count=False)
                
                # If the line number is starting fresh, then don't treat the previous range as part of this range (since we are starting fresh)
                if line_number_range.line_number_start.number <= 1:
                    previous_line_number_division = None
                    previous_line_number_range = None
                
                # If this is for a division title containing a line number, then set the start number for the current division and set the previous division accordingly
                if division.type in ["card"] and division.descriptor is not None and LineNumber.is_line_number( str(division.descriptor) ):
                    
                    # Set the start of the current line number
                    # We want this value to override whatever we already determined
                    line_number_range.line_number_start = LineNumber(str(division.descriptor))
                    
                    # Set the previous division to the new start line minus one
                    if previous_line_number_division is not None:
                        next_line_number = line_number_range.line_number_start.copy()
                        next_line_number.decrement()
                        previous_line_number_range.line_number_end = next_line_number
                        
                        if previous_line_number_range.makes_sense():
                            
                            previous_line_number_division.title = previous_line_number_range.get_line_count_title()
                            previous_line_number_division.title_slug = slugify(previous_line_number_division.title)
                            previous_line_number_division.descriptor = str(previous_line_number_range.line_number_start.number)
                            previous_line_number_division.save()
                
                # Ok, lets update the previous division
                elif previous_line_number_division is not None and line_number_range.line_number_start is not None and line_number_range.line_number_start.number > 0 and line_number_range.line_number_end.number > 0:
                    
                    # Set the division title if we have a division to update
                    previous_line_number_range.line_number_end = line_number_range.line_number_start.copy()
                    previous_line_number_range.line_number_end.decrement()
                    
                    if previous_line_number_range.makes_sense():
                        previous_line_number_division.title = previous_line_number_range.get_line_count_title()
                        previous_line_number_division.title_slug = slugify(previous_line_number_division.title)
                        previous_line_number_division.descriptor = str(previous_line_number_range.line_number_start.number)
                        
                        # Save the division
                        previous_line_number_division.save()
                
                # Now, set the current division
                if line_number_range.makes_sense():
                    division.title = line_number_range.get_line_count_title()
                    division.title_slug = slugify(division.title)
                    division.descriptor = str(line_number_range.line_number_start.number)
                    division.save()
                
                # Record the previous line count range set
                previous_line_number_range = line_number_range.copy()
                previous_line_number_division = division
                    
                # Restart the line count for the next division
                line_number_range.reset_start_line_count()
        
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
            
            original_content = division.original_content.encode('utf-8')
            division_doc = parseString(original_content)
            
            root_node = division_doc.getElementsByTagName(PerseusTextImporter.CHAPTER_TAG_NAME)[0]
            
            try:
                return self.import_verse_content( division, root_node, state_set)
        
            finally:
                division_doc.unlink()
                del(division_doc)
        
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
        
        try:
            return resulting_content
        finally:
            verse_doc.unlink()
            del(verse_doc)
        
    @staticmethod
    def get_line_count_recursive(node, line_number):
        
        numbering_reset = False
        
        # If the node it a paragraph or line, then increment the line number
        if node.nodeType == minidom.Element.ELEMENT_NODE and node.tagName in ["p", "l"]:
            line_number.increment()
        
        # If the node is a milestone then get it
        if node.nodeType == minidom.Element.ELEMENT_NODE and node.tagName == "milestone" and node.hasAttribute("n"):
            
            # Set the line number according to the attribute of the milestone
            new_line_number = LineNumber(value=node.attributes["n"].value)
            
            # Log if the value is not was is expected. This may indicate that a line element was not found that should have been.
            if new_line_number.number in [0, 1]:
                logger.warning("A line element indicated that the line numbering is restarting, line_number=%s, expected_line_number=%r" % ( str(new_line_number), line_number) )
                numbering_reset = True
            
            if new_line_number is not None and str(new_line_number) != line_number:
                logger.warning("A line element indicated the current line number and it did not match the expected value, line_number=%s, expected_line_number=%r" % ( str(new_line_number), str(line_number)) )
        
            # Update the line number
            if new_line_number is not None:
                line_number = new_line_number
            
        # Recurse on the children
        for child_node in node.childNodes:
            line_number, numbering_reset_new = PerseusTextImporter.get_line_count_recursive(child_node, line_number)
            
            if numbering_reset_new:
                numbering_reset = True
        
        return line_number, numbering_reset
    
    @staticmethod
    def get_line_count(verse_doc, count=None):
        """
        Get the line count from the provided verse element.
        
        Arguments:
        verse_doc -- The verse element to count up the line elements
        count -- The current count
        """
        
        restart_numbering_at_one = False
        
        if count is not None:
            line_number = LineNumber(value=str(count))
        else:
            line_number = LineNumber()
        
        # Get the line count nodes
        line_nodes = verse_doc.getElementsByTagName("l")
        
        # Use the line node elements if they exist
        if line_nodes is not None and len(line_nodes) > 0:
            
            # Handle each line count element
            for line_node in line_nodes:
                
                line_number.increment()
                
                # If the line indicates which number it is, then load this value
                if line_node.hasAttribute("n") and line_node.attributes["n"].value not in ["tr"]:
                    
                    # Get the specified value
                    new_line_count = line_node.attributes["n"].value
                    
                    # Log if the value is not was is expected. This may indicate that a line element was not found that should have been.
                    new_line_number = LineNumber(value=new_line_count)
                    
                    if new_line_number.number in [0, 1]:
                        logger.warning("A line element indicated that the line numbering is restarting, line_number=%s, expected_line_number=%r" % ( str(count), new_line_count) )
                        restart_numbering_at_one = True
                        
                    elif str(new_line_number) != line_number:
                        logger.warning("A line element indicated the current line number and it did not match the expected value, line_number=%s, expected_line_number=%r" % ( str(count), new_line_count) )
                
                    # Update the line number
                    line_number = new_line_number
        
        # Try to use the milestones otherwise
        else:
            line_number, restart_numbering_at_one_latest = PerseusTextImporter.get_line_count_recursive(verse_doc.documentElement, line_number)
            
            if restart_numbering_at_one_latest:
                restart_numbering_at_one = True
            
        # Return the line number
        return line_number, restart_numbering_at_one
    
    def update_line_count_info(self, document, line_number_range, reset_start_line_count=False):
        """
        Update the line count in case the readable units are to be named after the lines included.
        """
        
        # Get the updated line count
        new_line_number, restart_numbering_at_one = PerseusTextImporter.get_line_count(document, line_number_range.line_number_end)
        
        if new_line_number is not None and new_line_number.number > 0:
            # Set the updated line count
            line_number_range.line_number_end = new_line_number
        
        # Restart the numbering
        if restart_numbering_at_one:
            line_number_range.line_number_start.number = 1
        
        # Reset the line count if requested
        if reset_start_line_count:
            line_number_range.reset_start_line_count()
            
        return line_number_range
        
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
        
        # At this point, we have three variables that are important for keeping straight in order to ensure that the correct content gets appended:
        # 
        #   new_verse_node:  a new verse node. If not null, then it will become the next parent
        #   parent_node:     the node to attach the XML to
        #   next_level_node: the node that is passed to recursive calls as the next parent
        
        # Process each node
        for node in content_node.childNodes:
            
            # This determines if the content is ought to be attached to a verse
            attach_xml_content = True
            
            # This indicates if we ought to recurse down this node
            recurse_down_node = recurse
            
            if node.nodeType == minidom.Element.PROCESSING_INSTRUCTION_NODE:
                pass
            
            if node.nodeType == node.TEXT_NODE:
                
                # We need to see a milestone before we can set the text for a verse
                
                if len(node.data.strip()) > 0:
                    
                    # Start importing the verse if we got a division start but not a verse marker (which is possible)
                    if import_context.verse is None and import_context.division is not None:
                        self.make_verse(import_context, save=False)
                        
                        verses_created = verses_created + 1
                    
                        #import_context.verse = self.make_verse(save=False, division=division)
                        logger.debug("Making new verse (since we have content for a verse but no verse itself), division=%s, title=%s", str(division.sequence_number), self.work.title )
                    
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
                
                # Get the verse indicator
                if "n" in node.attributes.keys():
                    import_context.verse.indicator = node.attributes["n"].value
                else:
                    import_context.verse.indicator = str(verses_created + 1)
                    logger.warn('Milestone observed that did not have an associated unit, the sequence number will be used instead, division=%s, verse=%s, title=%s', import_context.division.sequence_number, import_context.verse.indicator, self.work.title)
                
                import_context.verse.save()
                
                attach_xml_content = False
                verses_created = verses_created + 1
                
                # Start adding the content to the new verse
                new_verse_node = import_context.current_node
                parent_node = new_verse_node
                next_level_node = new_verse_node
                
                logger.debug("Making verse %s in division %s of %s", import_context.verse.indicator, str(import_context.division.sequence_number), self.work.title)
                
            elif node.tagName in ["milestone"]:
                # Include:
                #  1) milestone nodes that are not in the current state set in the XML
                attach_xml_content = True
                
            elif node.tagName == "list" and "type" in node.attributes.keys() and node.attributes["type"].value == "toc":
                logger.debug("Skipping attachment of a %s node", node.tagName)
                attach_xml_content =  False
                recurse_down_node = False
                
            elif node.tagName == "note" and "type" in node.attributes.keys() and node.attributes["type"].value == "title":
                logger.debug("Skipping attachment of a %s node", node.tagName)
                attach_xml_content =  False
                recurse_down_node = False
                
            elif node.tagName in ["head"]:
                # Don't include: 
                #  1) head tag since we already pulled this in when we got the division tag
                #  2) notes since we don't handle them yet
                attach_xml_content =  False
                recurse_down_node = False
                
            # Attach the content to the division if it is for the current verse
            if attach_xml_content:
                next_level_node = import_context.append_xml(node, parent_node)
                
            # Recurse on the child-nodes
            if recurse_down_node:
                verses_created_temp, created_verse_node = self.import_verse_content(division, node, state_set, import_context, parent_node=next_level_node, recurse=True)
                verses_created = verses_created + verses_created_temp
                
                if created_verse_node is not None:
                    new_verse_node = created_verse_node # Let's save this save so that we pass it up the upstream calls
                    parent_node = new_verse_node
                    next_level_node = new_verse_node
                
        # If this is the original call, then just return the number of verse created.
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
            return transform_text(text, self.work.language, return_as_unicode=True)
        else:
            return text
        
    def getSectionTitle(self, div_node):
        """
        Get the the title of a section from the head node if it exists.
        
        Arguments:
        div_node -- A div node
        """
        
        head = self.findTagInDivision(div_node, "head")
        
        if head is not None:
            return self.getText(head.childNodes, True, separator=" ")
        
    def findTagInDivision(self, node, tag_name, depth_limit=5, current_depth=0):
        
        # Recursion base case:
        if current_depth >= depth_limit:
            return
        
        # Look through the children
        for child in node.childNodes:
            
            if child.nodeType == minidom.Element.ELEMENT_NODE and child.tagName == tag_name:
                return child
            
            elif child.nodeType == minidom.Element.ELEMENT_NODE and child.tagName =="milestone":
                # We hit a milestone, none of the rest of the children are for this division
                return
            
            elif child.nodeType == minidom.Element.ELEMENT_NODE and (child.tagName in ["text"] or child.tagName.startswith("div")):
                pass #This is in a different division, so skip it
            
            else:
                result = self.findTagInDivision( child, tag_name, depth_limit, current_depth + 1)
                
                # Stop if we found a result
                if result:
                    return result
                
    def import_body_sub_node(self, content_node, state_set, import_context=None, recurse=True, parent_node=None):
        """
        Imports the content from the children of the given node (which ought to be in the body).
        
        Arguments:
        content_node -- The XML node containing the content; needs to be the body node or one of its the sub-nodes
        state_set -- A set of units that ought to be used to create the divisions and verse divisions.
        import_context -- An ImportContext instance; used for determining which book, division, and verse is being imported
        recurse -- Indicates if the sub-nodes of the given
        parent_node -- The node that the child nodes ought to be appended to. That is, this node ought to be the parent of the newly created node.
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
            if self.ignore_content_before_first_milestone and not import_context.get_custom_attribute("milestone_observed", False):
                append_xml_content = False
            else:
                append_xml_content = True
            
            # We have to handle several nodes here:
            #    * text content: add to the verse if it exists
            #    * milestone: if a division divider, then split accordingly
            #    * div#: indicates a new book, make a section accordingly
            #    * text: indicates a new major section in a book, make a section accordingly
            #    * everything else: add it to the current division XML content
            
            ###################################
            # Ignore XML processing instructions
            ###################################
            if node.nodeType == minidom.ProcessingInstruction.nodeType:
                pass
            
            ###################################
            # If the content is a text-node, then attach it the current division
            ###################################
            elif node.nodeType == minidom.Node.TEXT_NODE:
                
                if import_context.division is None:
                    # No division exists yet, skipping this verse
                    logger.debug("No division exists yet, skipping this content, title=%s, content=%s", self.work.title, node.data)
            
            ###################################
            # If the content is a comment, then just skip it
            ###################################
            elif node.nodeType == minidom.Node.COMMENT_NODE:
                append_xml_content = False # Skip comments
            
            ###################################
            # If the content is a text node with an "n" attribute then treat the node as a division
            ###################################
            elif node.tagName == "text" and node.attributes.get("n", None) != None:
                
                # Note that we have not observed a milestone yet in this division
                import_context.set_custom_attribute("milestone_observed", False)
                
                # Get the information about the section
                division_type = "text"
                descriptor = None
                
                if "n" in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                
                # Try to get a title node
                original_title = self.getSectionTitle(node)
                title = self.process_text(original_title)
                
                level = 0
                self.make_division(import_context, level, division_type=division_type, title=title, original_title=original_title, descriptor=descriptor)
                
                # Start adding the content to the new division
                new_division_node = import_context.current_node
                parent_node = new_division_node
                next_level_node = new_division_node
                
                logger.debug("Making division from a text node at level %i in %s" % (level, self.work.title))
                
                append_xml_content = False
            
            ###################################
            # If the content is a new milestone marker, then make a milestone
            ###################################
            elif node.tagName == "milestone" and self.is_milestone_chunk(state_set, node, self.only_last_state_is_non_chunk):
                
                # Note that we observed a milestone
                import_context.set_custom_attribute("milestone_observed", True)
                
                append_xml_content = False
                
                if 'n' in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                else:
                    descriptor = ""
                
                # Get the division type
                if 'unit' in node.attributes.keys():
                    division_type = node.attributes["unit"].value
                else:
                    division_type = None
                
                # Make the division
                self.make_division(import_context=import_context, descriptor=descriptor, state_info=self.get_state_for_milestone(state_set, node), division_type=division_type, level=10)
                logger.debug("Making division %s (since it is a chunk) of %s" % ( str(import_context.division.sequence_number), self.work.title))
                
                # Start adding the content to the new division
                new_division_node = import_context.current_node
                parent_node = new_division_node
                next_level_node = new_division_node
            
            ###################################
            # If the content is a verse marker and we don't have a division, then create one
            ###################################
            elif node.tagName == "milestone" and self.is_milestone_in_state_set(state_set, node):
                
                # Note that we observed a milestone
                import_context.set_custom_attribute("milestone_observed", True)
                append_xml_content = True
                
                if 'n' in node.attributes.keys():
                    descriptor = node.attributes["n"].value
                else:
                    descriptor = ""
                
                # If we have a verse without a division, then go ahead and make one
                if import_context.division is None:
                    self.make_division(import_context=import_context, descriptor=descriptor, state_info=self.get_state_for_milestone(state_set, node), level=10)
                    logger.debug("Making a division for %s since once does not exist yet (so that we can add a verse)" % (self.work.title))
                    
                    # Start adding the content to the new division
                    new_division_node = import_context.current_node
                    parent_node = new_division_node
                    next_level_node = new_division_node
            
            ###################################
            # Handle division nodes
            ###################################
            elif not self.ignore_division_markers and PerseusTextImporter.DIV_PARSE_REGEX.match( node.tagName ) and (self.division_tags is None or node.tagName in self.division_tags) :
                
                # Get the type of the section
                division_type = None
                
                if "type" in node.attributes.keys():
                    division_type = node.attributes["type"].value
                
                # Get the level from the tag name
                m = PerseusTextImporter.DIV_PARSE_REGEX.search( node.tagName )
                level = int(m.groupdict()['level'] )
                
                is_in_state_set = False
                
                # Get the state set associated with this entry
                for state in state_set:
                    if division_type is not None and state.name.lower() == division_type.lower() and state.level is not None:
                        level = state.level
                        is_in_state_set = True
                        break
                
                # Ignore the div if is not in the state set then ignore it we ought to
                if self.ignore_undeclared_divs and not is_in_state_set:
                    
                    # Ignore this one
                    pass
                
                else:
                    
                    # Note that we have not observed a milestone yet in this division
                    import_context.set_custom_attribute("milestone_observed", False)
                    
                    # Get the descriptor
                    descriptor = None
                    
                    if "n" in node.attributes.keys():
                        descriptor = node.attributes["n"].value
                    
                    original_title = self.getSectionTitle(node)
                    title = self.process_text(original_title)
                    
                    # Use the division type as the title to the type (in some cases)
                    if original_title is None and division_type is not None:
                        
                        # Set the title for intro divisions
                        if division_type == "intro":
                            original_title = "intro"
                            title = "Introduction"
                    
                    self.make_division(import_context, level, division_type=division_type, title=title, original_title=original_title, descriptor=descriptor)
                    
                    # Start adding the content to the new division
                    new_division_node = import_context.current_node
                    parent_node = new_division_node
                    next_level_node = new_division_node
                    
                    logger.debug("Made division at level %i in %s" % (level, self.work.title))
                    
                    append_xml_content = False
                
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
            self.close_division(import_context)
            return import_context.divisions
            
        return new_division_node