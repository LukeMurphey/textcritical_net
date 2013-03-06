import re
from django import template
from reader.shortcuts import convert_xml_to_html5, convert_xml_to_html5_minidom
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

@register.filter(name='perseus_xml_to_html5')
def perseus_xml_to_html5(value, language=None):
    """
    Converts the provided XML to HTML5 custom data attributes. Performs some changes specific to Perseus TEI documents.
    
    Usage:
    {{text|perseus_xml_to_html5:"Greek"}}
    """
    
    # Make the function to perform the transformation
    text_transformation_fx = lambda text, parent_node, dst_doc: transform_perseus_text(text, parent_node, dst_doc, language)
    
    converted_doc = convert_xml_to_html5( value, language=language, text_transformation_fx=text_transformation_fx, node_transformation_fx=transform_perseus_node )
    
    try:
        return converted_doc.toxml( encoding="utf-8" )
    finally:
        converted_doc.unlink()
        del(converted_doc)
    
def transform_perseus_node( tag, attrs, parent, dst_doc ):
    """
    Transform nodes to improve rendering. Specifically, this function will make note nodes able to be rendered with popovers.
    
    Arguments:
    tag -- The tag name of the node being examined
    attrs -- The attributes of the given node
    parent -- The parent node that this node is going to be placed under
    dst_doc -- The document of the converted document (to add new nodes to)
    """
    
    use_popovers = True
    use_icon = True
    
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
        
        parent.appendChild(note_tag)
        
        new_node = dst_doc.createElement( "span" )
        new_node.setAttribute( "class", "label note hide" )
        new_node.setAttribute( "id", "content_for_" + identifier )
        
        return new_node
    
    if tag == "note":
        new_node = dst_doc.createElement( "span" )
        new_node.setAttribute( "class", "label note" )
        
        return new_node
    
def transform_perseus_text(text, parent_node, dst_doc, default_language):
    """
    Transform the Perseus XML to HTML that can be easily displayed in a web app.
    
    Arguments:
    text -- The content of a text node to be processed
    parent_node -- The parent node within the converted document
    dst_doc -- The document of the converted document (to add new nodes to)
    default_language -- The language of the document (unless otherwise specified)
    """
    
    # Get the language specific to this node if is defined
    if parent_node is not None and parent_node.attributes.get('data-lang', None) is not None:
        language = parent_node.attributes['data-lang'].value
    else:
        language = default_language
    
    # Notes are typically in English and thus do not need transformed.
    if parent_node.attributes.get('class', None) is not None and 'note' in parent_node.attributes.get('class', '').value.split(' '):#and parent_node.attributes.get('class', None).value == "note":
        return text.encode('utf-8')
    
    # Split up the text and place the text segments in nodes
    segments = re.findall("[\s]+|[\[\],.:.;]|[^\s\[\],.:.;]+", text)
    #segments = text.split(" ")
    
    for s in segments:
        
        # Don't wrap punctuation in a word node
        if s in [";", ",", ".", "[", "]", ":"] or len(s.strip()) == 0:
            txt_node = dst_doc.createTextNode( s )
            parent_node.appendChild( txt_node )
        
        else:
            new_node = dst_doc.createElement( "span" )
            new_node.setAttribute( "class", "word" )
            
            # Create the text node and append it
            txt_node = dst_doc.createTextNode( transform_text(s, language).decode( "utf-8" ) )
            new_node.appendChild(txt_node)
           
            # Append the node
            parent_node.appendChild(new_node)