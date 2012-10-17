from django import template
from reader.shortcuts import convert_xml_to_html5
from reader.language_tools import transform_text

import xml.dom.minidom as minidom

register = template.Library()

def xml_to_html5(value, language=None):
    """Converts the provided XML to HTML5 custom data attributes."""
    
    doc = minidom.parseString(value)
    converted_doc = convert_xml_to_html5( doc, language=language )
    
    return converted_doc.toxml( encoding="utf-8" )

def perseus_xml_to_html5(value, language=None):
    
    # Make the function to perform the transformation
    text_transformation_fx = lambda text, parent_node: transform_perseus_text(text, parent_node, language)
    
    doc = minidom.parseString(value)
    converted_doc = convert_xml_to_html5( doc, language=language,  text_transformation_fx=text_transformation_fx )
    
    return converted_doc.toxml( encoding="utf-8" )
    
def transform_perseus_text(text, parent_node, language):
    
    if parent_node.tagName.startswith("div"):
        pass
    
    if parent_node.tagName in ["body", "p", "title", "foreign"]:
        pass

    else:
        return text
    
    return transform_text(text, language)
    
register.filter('xml_to_html5', xml_to_html5)