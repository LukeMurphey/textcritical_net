import xml.dom.minidom as minidom
from reader.language_tools.greek import Greek

def transform_text( text, language ):
    """
    Convert the content according to the rules necessary to make the content work for the given language.
    
    Arguments:
    text -- the text to convert
    language -- the language to use for applying the conversion rules
    """
    
    # Don't try to process a null string as this will fail
    if text is None:
        return None
    
    # Convert Greek beta code
    if language == "Greek":
        text_unicode = Greek.beta_code_to_unicode(text)
        
        return text_unicode.encode('utf-8')
    
    # By default, just return the text
    else:
        return text

def convert_xml_to_html5( src_doc, new_root_node_tag_name=None, text_transformation_fx=None, language=None, return_as_str=False, allow_closing_in_start_tag=False):
    """
    Convert the XML into HTML5 with custom data attributes.
    
    Arguments:
    document -- An XML document containing the original XML to be converted
    new_root_node_tag_name -- The name of the root node (otherwise, the root node will be converted too).
    text_transformation_fx -- A function which will be applied to all text. The function must take the following parameters: the text to transform, the tag_name of the parent node
    language -- the language to use for transforming the text. This will only be used if text_transformation_fx is not none in which case the transform_text function will be used
    return_as_str -- If true, then the content will be returned as a string; otherwise a document will be returned
    allow_closing_in_start_tag -- If true, then nodes with no children will be closed without an explicit closing tag. Otherwise, they will include an explicit closing tag.
    """
    
    # If the language was provided but a text transformation function was not, then use the process_text function
    if text_transformation_fx is None and language is not None:
        text_transformation_fx = lambda text, parent_node: transform_text(text, language)
    
    # Parse the original content
    root_node_src = src_doc.firstChild
    
    # Make the new document
    dst_doc = minidom.Document()
    
    # Use the existing root node unless a new tag name is provided
    if new_root_node_tag_name is None:
        root_node_dst = dst_doc.createElement( "span" )
        root_node_dst.setAttribute( "class", root_node_src.tagName)
    else:
        root_node_dst = dst_doc.createElement(new_root_node_tag_name)
    
    dst_doc.appendChild(root_node_dst)
    
    # Convert it
    for child in root_node_src.childNodes:
        add_xml_as_html( src_doc                    = src_doc,
                         src_node                   = child,
                         dst_doc                    = dst_doc,
                         parent_dst_node            = root_node_dst,
                         language                   = language,
                         text_transformation_fx     = text_transformation_fx,
                         allow_closing_in_start_tag = allow_closing_in_start_tag)
    
    # Return the result
    if return_as_str:
        return dst_doc.toxml( encoding="utf-8" )
    else:
        return dst_doc
    
def add_xml_as_html( src_doc, src_node, dst_doc, parent_dst_node, language, text_transformation_fx = None, allow_closing_in_start_tag=False ):
    new_dst_node = None
    
    # Handle the text node
    if src_node.nodeType == minidom.Node.TEXT_NODE:
        
        # Transform the content if a transform function is provided
        if text_transformation_fx is not None:
            content = text_transformation_fx( text=src_node.data, parent_node=src_node.parentNode ).decode( "utf-8" )
        else:
            content = src_node.data
            
        # Create the text node
        new_dst_node = dst_doc.createTextNode( content )
        parent_dst_node.appendChild(new_dst_node)
        
    # Handle the comment node (skip it)
    elif src_node.nodeType == minidom.Node.COMMENT_NODE:
        pass # Don't copy comments over
    
    # Copy the other nodes
    else:
        new_dst_node = dst_doc.createElement( "span" )
        new_dst_node.setAttribute( "class", src_node.tagName)
        
        # Copy over the attributes
        for name, value in src_node.attributes.items():
            new_dst_node.setAttribute( "data-" + name, value)
        
        # Add the node
        parent_dst_node.appendChild(new_dst_node)
        
        # If we don't allow closing in start tags, then add a text node that is empty to prevent it from closing early 
        if not allow_closing_in_start_tag and len(src_node.childNodes) == 0:
            txt_node = dst_doc.createTextNode( "" )
            new_dst_node.appendChild(txt_node)
        
    # Recurse on the child nodes
    for child_node in src_node.childNodes:
        add_xml_as_html(src_doc, child_node, dst_doc, new_dst_node, language, text_transformation_fx)