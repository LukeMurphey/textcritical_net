import re
from django import template
from reader.shortcuts import convert_xml_to_html5, convert_xml_to_html5_minidom
from xml.dom import minidom
from reader.language_tools import transform_text
import random

register = template.Library()

@register.filter(name='xml_to_html5')
def xml_to_html5(value, language=None):
    """
    Converts the provided XML to HTML5 custom data attributes.
    
    Usage:
    {{text|xml_to_html5:"Greek"}}
    """
    
    value = value.encode('utf-8')
    
    converted_doc = convert_xml_to_html5( value, language=language )
    
    try:
        return converted_doc.firstChild.toxml( encoding="utf-8" )
    finally:
        converted_doc.unlink()
        del(converted_doc)

@register.filter(name='unbound_text_to_html5')
def unbound_text_to_html5(text, language=None):
    """
    Converts the provided text to HTML5 custom data attributes.
    
    Usage:
    {{text|unbound_text_to_html5:"Greek"}}
    """
    
    # Make the document that will contain the verse
    converted_doc = minidom.Document()
    
    # Make the verse node to attach the content to
    verse_node = converted_doc.createElement( "span" )
    verse_node.setAttribute("class", "verse")
    
    # Append the 
    converted_doc.appendChild(verse_node)
    
    # Split up the text and place the text segments in nodes
    segments = re.findall("[\s]+|[\[\],.:.;]|[^\s\[\],.:.;]+", text)
    
    for s in segments:
        
        # Don't wrap punctuation in a word node
        if s in [";", ",", ".", "[", "]", ":"] or len(s.strip()) == 0:
            txt_node = converted_doc.createTextNode( s )
            verse_node.appendChild( txt_node )
        
        else:
            word_node = converted_doc.createElement( "span" )
            word_node.setAttribute( "class", "word" )
            
            # Create the text node and append it
            if language is None:
                txt_node = converted_doc.createTextNode( s )
            else:
                txt_node = converted_doc.createTextNode( transform_text(s, language).decode( "utf-8" ) )
            
            word_node.appendChild(txt_node)
           
            # Append the node
            verse_node.appendChild(word_node)
    
    return converted_doc.toxml( encoding="utf-8" )

@register.filter(name='perseus_xml_to_html5')
def perseus_xml_to_html5(value, language=None):
    """
    Converts the provided XML to HTML5 custom data attributes. Performs some changes specific to Perseus TEI documents.
    
    Usage:
    {{text|perseus_xml_to_html5:"Greek"}}
    """
    
    return transform_perseus_xml_to_html5(value, language, True).replace('<?xml version="1.0" encoding="utf-8"?>', "")
        
def transform_perseus_xml_to_html5(xml_text, language=None, return_as_str=False):
    """
    Converts the provided XML to HTML5 custom data attributes. Performs some changes specific to Perseus TEI documents.
    """
    
    # Make the function to perform the transformation
    text_transformation_fx = lambda text, parent_node, dst_doc: transform_perseus_text(text, parent_node, dst_doc, language)
    
    converted_doc = convert_xml_to_html5( xml_text, language=language, text_transformation_fx=text_transformation_fx, node_transformation_fx=transform_perseus_node )
    
    try:
        if return_as_str:
            return converted_doc.toxml( encoding="utf-8" )
        else:
            return converted_doc
    finally:
        converted_doc.unlink()
        del(converted_doc)
        
@register.filter(name='perseus_xml_to_epub_html5')
def perseus_xml_to_epub_html5(value, arg=None):
    """
    Converts the provided XML to HTML5 custom data attributes. Performs some changes specific to Perseus TEI documents.
    
    Usage:
    {{text|perseus_xml_to_epub_html5:"Greek"}}
    
    This example provides the initial note number
    {{text|perseus_xml_to_epub_html5:"Greek,5"}}
    """
    
    if "," in arg:
        language, note_number = arg.split(",")
        note_number = int(note_number)
    else:
        note_number = 1
        language = arg
    
    return transform_perseus_xml_to_epub_html5(value, language, True, note_number_start=note_number).replace('<?xml version="1.0" encoding="utf-8"?>', "")
        
def transform_perseus_xml_to_epub_html5(xml_text, language=None, return_as_str=False, note_number_start=1):
    """
    Converts the provided XML to HTML5 custom data attributes. Performs some changes specific to Perseus TEI documents.
    """
    
    # Make the function to perform the transformation
    text_transformation_fx = lambda text, parent_node, dst_doc: transform_perseus_text(text, parent_node, dst_doc, language, disable_wrapping=True)
    next_note_number = NoteNumber(note_number_start)
    transform_node = lambda tag, attrs, parent, dst_doc: transform_perseus_node(tag, attrs, parent, dst_doc, False, False, next_note_number)
    
    converted_doc = convert_xml_to_html5( xml_text, language=language, text_transformation_fx=text_transformation_fx, node_transformation_fx=transform_node )
    
    try:
        if return_as_str:
            return converted_doc.toxml( encoding="utf-8" )
        else:
            return converted_doc
    finally:
        converted_doc.unlink()
        del(converted_doc)
    
@register.filter(name='count_note_nodes')
def count_note_nodes( value, previous_count=None ):
    
    if previous_count is not None:
        previous_count = int(previous_count)
    else:
        previous_count = 0
        
    return previous_count + len(re.findall('[<]note', value))
    
@register.filter(name='increment_note_count')
def increment_note_count( value, amount ):
    
    amount = int(amount)
    
    return value.increment(amount)
    
class NoteNumber(object):
    
    def __init__(self, n = 1):
        self.number = n
    
    def __str__(self):
        return str(self.number)
        
    def value(self):
        return str(self.number)
        
    def increment(self, amount=1):
        
        if amount != 1:
            amount = int(amount)
        
        self.number = self.number + amount
        return self.number
    
def transform_perseus_node( tag, attrs, parent, dst_doc, use_popovers=True, use_icon=True, next_note_number=None ):
    """
    Transform nodes to improve rendering. Specifically, this function will make note nodes able to be rendered with popovers.
    
    Arguments:
    tag -- The tag name of the node being examined
    attrs -- The attributes of the given node
    parent -- The parent node that this node is going to be placed under
    dst_doc -- The document of the converted document (to add new nodes to)
    """
    
    # If the notes should be rendered with popovers
    if use_popovers and tag == "note":
        
        identifier = '%08x' % random.randrange(256**4)
        
        if use_icon:
            note_tag = dst_doc.createElement( "i" )
            note_tag.setAttribute( "class", "icon-info-sign icon-white note-tag" )
            note_tag.setAttribute( "id", identifier )
            
            txt_node = dst_doc.createTextNode("")
            note_tag.appendChild(txt_node)
        else:
            note_tag = dst_doc.createElement( "span" )
            note_tag.setAttribute( "class", "label label-success note-tag" )
            note_tag.setAttribute( "id", identifier )
            
            txt_node = dst_doc.createTextNode("Note")
            note_tag.appendChild(txt_node)
            
        # Add the attribute number so that it can be added to the title of the note
        for attr in attrs:
            if attr[0] == 'n':
                note_tag.setAttribute( "data-note-number", attr[1] )
        
        parent.appendChild(note_tag)
        
        new_node = dst_doc.createElement( "span" )
        new_node.setAttribute( "class", "label note hide" )
        new_node.setAttribute( "id", "content_for_" + identifier )
        
        return new_node
    
    elif tag == "note":
        
        # Make the link tag to the footnote
        href_node = dst_doc.createElement( "a" )
        href_node.setAttribute( "href", "#note_content_" +  str(next_note_number))
        href_node.setAttribute( "name", "note_anchor_" +  str(next_note_number))
        parent.appendChild(href_node)
        
        # Create the note indicator
        new_node = dst_doc.createElement( "sup" )
        new_node.setAttribute( "class", "note" )
        href_node.appendChild(new_node)
        
        # If a note number object is included, then just assign the note
        if next_note_number is not None:            
            
            # Create the text node with the note number
            txt_node = dst_doc.createTextNode( str(next_note_number) )
            new_node.appendChild(txt_node)
            
            # Increment the note number so that the next note has the next number
            next_note_number.increment()
            
            # Make a node to hide the underlying content
            note_content_node = dst_doc.createElement( "span" )
            note_content_node.setAttribute( "class", "hide" )
            new_node.appendChild(note_content_node)
            
            return note_content_node
        
        return new_node
    
def transform_perseus_text(text, parent_node, dst_doc, default_language, disable_wrapping=False):
    """
    Transform the Perseus XML to HTML that can be easily displayed in a web app.
    
    Arguments:
    text -- The content of a text node to be processed
    parent_node -- The parent node within the converted document
    dst_doc -- The document of the converted document (to add new nodes to)
    default_language -- The language of the document (unless otherwise specified)
    disable_wrapping -- If true, then words will not be wrapped in <span> XML nodes
    """

    # Get the language specific to this node if is defined
    if parent_node is not None and parent_node.attributes.get('data-lang', None) is not None:
        language = parent_node.attributes['data-lang'].value
    else:
        language = default_language
    
    # Notes are typically in English and thus do not need transformed.
    if parent_node is not None and parent_node.attributes.get('class', None) is not None and 'note' in parent_node.attributes.get('class', '').value.split(' '):#and parent_node.attributes.get('class', None).value == "note":
        return text.encode('utf-8')
    
    # Don't split up the words for English documents since we don't allow morphological lookups on English
    if language.lower() == "english":
        return text.encode('utf-8')
    
    elif disable_wrapping:
        return transform_text(text, language, True).encode('utf-8')
           
    else:
       
        # Split up the text and place the text segments in nodes
        segments = re.findall("[\s]+|[\[\],.:.;]|[^\s\[\],.:.;]+", text)
        
        for s in segments:
            
            # Don't wrap punctuation in a word node
            if s in [";", ",", ".", "[", "]", ":"] or len(s.strip()) == 0:
                txt_node = dst_doc.createTextNode( s )
                parent_node.appendChild( txt_node )
            
            else:
                new_node = dst_doc.createElement( "span" )
                new_node.setAttribute( "class", "word" )
                
                # Create the text node and append it
                txt_node = dst_doc.createTextNode( transform_text(s, language, True) )
                new_node.appendChild(txt_node)
               
                # Append the node
                parent_node.appendChild(new_node)
              
def is_hidden(node):

    if node.nodeName == "sup" or node.nodeName == "span":
        
        if node.attributes.get('class', None) != None:
            
            classes = node.attributes.get('class', None).value.split(" ")
        
            if "hide" in classes:
                return True
            
    else:
        return False
              
@register.filter(name='prune_hidden')
def prune_hidden(xml_str):
    
    # Parse the XML
    doc = minidom.parseString(xml_str)
    
    # Make the prune function
    fx_should_prune = is_hidden
        
    # Prune the nodes
    prune_nodes( doc, None, fx_should_prune)
    
    # Convert the content back to xml
    xml_str_after = doc.toxml()
    
    # Remove the XML info
    return xml_str_after.replace('<?xml version="1.0" ?>', "")
    
def prune_nodes(node, parent, fx_should_prune):
    
    if fx_should_prune(node) and parent is not None:
        parent.removeChild(node)
        
        # Indicate that the node was pruned
        return True
    
    elif node.hasChildNodes():
        for n in node.childNodes:
            prune_nodes(n, node, fx_should_prune)
            
        return False
            
              
@register.filter(name='simplify_person_name')
def simplify_person_name( name ):
    """
    Simpify a name to a last name only. Titles such as Ph. D. will be removed first.
    
    Arguments:
    name -- The name to shorten
    """
    
    if name is not None:
        new_name = name.replace("Ph.D.", "").replace("Ph. D.", "").replace("M.A.", "").replace("LL.D.", "").replace("A.M.", "").replace("Esq.", "").replace(",", "").strip()
        
        return new_name.split(" ")[-1]
        
    else:
        return name