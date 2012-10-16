from django import template
from reader.shortcuts import convert_xml_to_html5
import xml.dom.minidom as minidom

register = template.Library()

def xml_to_html5(value, language=None):
    """Converts the provided XML to HTML5 custom data attributes."""
    
    doc = minidom.parseString(value)
    converted_doc = convert_xml_to_html5( doc, language=language )
    
    return converted_doc.toxml( encoding="utf-8" )

register.filter('xml_to_html5', xml_to_html5)