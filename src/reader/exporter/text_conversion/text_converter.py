from six.moves.html_parser import HTMLParser
from collections import OrderedDict

class TextConverter(HTMLParser):
    """
    Takes an TEI XML document and produces a text version.
    """
    
    class Note(object):
        def __init__(self, number, value):
            self.number = number
            self.value = value
    
    def __init__(self, note_number=1, include_notes_at_end=False):
        """
        Initialize the text converter.
        """

        self.include_notes_at_end = include_notes_at_end
        
        # Initialize the location where the notes will be
        self.text_doc = ''
        
        # If a tag is set to ignore those below this point, then this stack will track the point until the
        self.ignore_tag_stack = None
        
        # Store some things for keeping notes around
        self.note_number = note_number
        self.notes = OrderedDict()
        self.current_note = ''

        # Initialize the base class
        HTMLParser.__init__(self)
        
    def is_in_note_tag_state(self):
        if self.ignore_tag_stack is None:
            return False

        return len(self.ignore_tag_stack) > 0

    def get_attr(self, attrs, attribute_name):
        for attr in attrs:
            name = attr[0]
            value = attr[1]
            
            if name == attribute_name:
                return value
            
    def has_classname(self, attrs, classname):
        class_attr = self.get_attr(attrs, "class")
        
        if class_attr is None:
            return False
        
        classnames = class_attr.split(" ")
        
        return classname in classnames

    def is_note_tag(self, tag, attrs):
        if tag == "span" and self.has_classname(attrs, "note"):
            return True
        
        return False

    def handle_starttag(self, tag, attrs):
        # If we are in a state in which we should ignore these tags, then add the current one so that we can track when
        # to leave this state
        if(self.is_in_note_tag_state()):
            self.ignore_tag_stack.append(tag)
        
        # Determine if this is a tag to start ignoring
        elif(self.is_note_tag(tag, attrs)):

            # Add in a placeholder for the note
            self.text_doc = self.text_doc + "[" + str(self.note_number) + "]"
            
            # If we are to ignore this, then add it to the list so start ignoring this sub-tree
            self.ignore_tag_stack = [tag]

    def handle_endtag(self, tag):
        if self.is_in_note_tag_state():
            self.ignore_tag_stack.pop()
            
            # If this is the last tag, then register the note and prep for the next one
            if len(self.ignore_tag_stack) == 0:
                self.notes[self.note_number] = self.current_note
                self.current_note = ''
                self.note_number += 1
            
    def handle_data(self, data):
        if not self.is_in_note_tag_state():
            self.text_doc = self.text_doc + data
        else:
            self.current_note = self.current_note + data
            
    def feed(self, data):
        # Process the text
        HTMLParser.feed(self, data)
        
        # Add in the footnotes
        if self.include_notes_at_end:
            if len(self.notes) > 0:
                self.text_doc = self.text_doc + "\nFootnotes:"
            
            for note_number, text in self.notes.items():
                self.text_doc = self.text_doc + "\n[" + str(note_number) + "] " + text
