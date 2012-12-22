import re
from django import template
from reader.shortcuts import convert_xml_to_html5, convert_xml_to_html5_minidom
from reader.language_tools import transform_text

register = template.Library()

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

def perseus_xml_to_html5(value, language=None):
    """
    Converts the provided XML to HTML5 custom data attributes. Performs some changes specific to Perseus TEI documents.
    
    Usage:
    {{text|perseus_xml_to_html5:"Greek"}}
    """
    
    # Make the function to perform the transformation
    text_transformation_fx = lambda text, parent_node, dst_doc: transform_perseus_text(text, parent_node, dst_doc, language)
    
    converted_doc = convert_xml_to_html5( value, language=language, text_transformation_fx=text_transformation_fx )
    
    try:
        return converted_doc.toxml( encoding="utf-8" )
    finally:
        converted_doc.unlink()
        del(converted_doc)
    
def transform_perseus_text(text, parent_node, dst_doc, default_language):
    
    # Get the language specific to this node if is defined
    if parent_node is not None and parent_node.attributes.get('data-lang', None) is not None:
        language = parent_node.attributes['data-lang'].value
    else:
        language = default_language
    
    # Notes are typically in English and thus do not need transformed.
    if parent_node.attributes.get('class', None) is not None and parent_node.attributes.get('class', None).value == "note":
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
            new_node.setAttribute( "class", "word")
            
            # Create the text node and append it
            txt_node = dst_doc.createTextNode( transform_text(s, language).decode( "utf-8" ) )
            new_node.appendChild(txt_node)
           
            # Append the node
            parent_node.appendChild(new_node)
    
register.filter('xml_to_html5', xml_to_html5)
register.filter('perseus_xml_to_html5', perseus_xml_to_html5)