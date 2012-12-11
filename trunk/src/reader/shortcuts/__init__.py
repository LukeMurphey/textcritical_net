import xml.dom.minidom as minidom
from reader.language_tools.greek import Greek
from reader.language_tools import transform_text

from HTMLParser import HTMLParser
from xml.dom.minidom import parseString
from htmlentitydefs import name2codepoint

class HTML5Converter(HTMLParser):
    """
    Takes an XML document and produces a HTML5 document that can be posted within an HTML document.
    """
    
    def __init__(self, new_root_node_tag_name, allow_closing_in_start_tag, text_transformation_fx, node_transformation_fx):
        """
        Initialize the HTML5 converter.
        
        Arguments:
        new_root_node_tag_name -- The name of the root node (otherwise, the root node will be converted too).
        allow_closing_in_start_tag -- If true, then nodes with no children will be closed without an explicit closing tag. Otherwise, they will include an explicit closing tag.
        text_transformation_fx -- A function which will be applied to all text. The function must take the following parameters: the text to transform, the tag_name of the parent node
        node_transformation_fx -- A function that allows node transformations to be overridden. The function must take the following parameters: tag name, attributes, parent node, document
        """
        
        self.new_root_node_tag_name = new_root_node_tag_name
        self.text_transformation_fx = text_transformation_fx
        self.node_transformation_fx = node_transformation_fx
        self.allow_closing_in_start_tag = allow_closing_in_start_tag
        
        # Make the new document
        self.dst_doc = minidom.Document()
        
        # This is the node we are attaching content to
        self.current_node = None
        
        # Indicates the number of nodes processed
        self.nodes_processed = 0
        
        # initialize the base class
        HTMLParser.__init__(self)
    
    def handle_starttag(self, tag, attrs):
        
        parent = self.current_node
        custom_current_node = None
        
        # Use a different root node if we were directed to use one
        if self.new_root_node_tag_name is not None and self.nodes_processed == 0:
            self.current_node = self.dst_doc.createElement(self.new_root_node_tag_name)
            
        else:
            
            # Use the node transformation function if it is defined
            if self.node_transformation_fx is not None:
                custom_current_node = self.node_transformation_fx( tag, attrs, parent, self.dst_doc)
                
            # If the transformation function didn't handle the node, then process it normally
            if custom_current_node is None:
                self.current_node = self.dst_doc.createElement( "span" )
                self.current_node.setAttribute( "class", tag)
            else:
                self.current_node = custom_current_node
        
        # Copy over the attributes
        if custom_current_node is None:
            for name, value in attrs:
                self.current_node.setAttribute( "data-" + name, value)
            
        # Attach the new node
        if parent is not None:
            parent.appendChild(self.current_node)
        else:
            self.dst_doc.appendChild(self.current_node)
            
        self.nodes_processed = self.nodes_processed + 1
        
    def handle_endtag(self, tag):
        
        # If we don't allow closing in start tags, then add a text node that is empty to prevent it from closing early 
        if not self.allow_closing_in_start_tag and len(self.current_node.childNodes) == 0:
            txt_node = self.dst_doc.createTextNode( "" )
            self.current_node.appendChild(txt_node)
            
        # Move the current pointer up one
        self.current_node = self.current_node.parentNode
    
    def handle_data(self, data):
        
        # Don't try to add a node if we don't have a parent
        if self.current_node is None:
            return
        
        # Transform the content if a transform function is provided
        if self.text_transformation_fx is not None:
            txt_node = self.dst_doc.createTextNode( self.text_transformation_fx( text=data, parent_node=self.current_node ).decode( "utf-8" ) )
        else:
            txt_node = self.dst_doc.createTextNode( data )

        # Append the txt node
        self.current_node.appendChild(txt_node)

    def handle_comment(self, data):
        pass
    
    def handle_entityref(self, name):
        
        # Make a text node to handle the content
        txt_node = self.dst_doc.createTextNode( unichr(name2codepoint[name]) )

        # Append the txt node
        self.current_node.appendChild(txt_node)
        
    def handle_charref(self, name):
        if name.startswith('x'):
            c = unichr(int(name[1:], 16))
        else:
            c = unichr(int(name))
            
        # Make a text node to handle the content
        txt_node = self.dst_doc.createTextNode( c )

        # Append the txt node
        self.current_node.appendChild(txt_node)

class BootstrapCustomizer():
    
    def node_transformation_fx(self, tag, attrs, parent, document ):
        pass

def convert_xml_to_html5( xml_str, new_root_node_tag_name=None, text_transformation_fx=None, language=None, return_as_str=False, allow_closing_in_start_tag=False, node_transformation_fx=None):
    """
    Convert the XML into HTML5 with custom data attributes.
    
    Arguments:
    xml_str -- An XML document containing the original XML to be converted
    new_root_node_tag_name -- The name of the root node (otherwise, the root node will be converted too).
    text_transformation_fx -- A function which will be applied to all text. The function must take the following parameters: the text to transform, the tag_name of the parent node
    language -- the language to use for transforming the text. This will only be used if text_transformation_fx is not none in which case the transform_text function will be used
    return_as_str -- If true, then the content will be returned as a string; otherwise a document will be returned
    allow_closing_in_start_tag -- If true, then nodes with no children will be closed without an explicit closing tag. Otherwise, they will include an explicit closing tag.
    node_transformation_fx -- A function that allows node transformations to be overridden. The function must take the following parameters: tag name, attributes, parent node, document
    """
    
    # If the language was provided but a text transformation function was not, then use the process_text function
    if text_transformation_fx is None and language is not None:
        text_transformation_fx = lambda text, parent_node: transform_text(text, language)
    
    # Convert the content
    converter = HTML5Converter(new_root_node_tag_name, allow_closing_in_start_tag, text_transformation_fx, node_transformation_fx)
    converter.feed(xml_str)
    
    # Return the result
    if return_as_str:
        return converter.dst_doc.toxml( encoding="utf-8" )
    else:
        return converter.dst_doc
    

def convert_xml_to_html5_minidom( xml_str, new_root_node_tag_name=None, text_transformation_fx=None, language=None, return_as_str=False, allow_closing_in_start_tag=False):
    """
    Convert the XML into HTML5 with custom data attributes.
    
    Arguments:
    xml_str -- An XML document containing the original XML to be converted
    new_root_node_tag_name -- The name of the root node (otherwise, the root node will be converted too).
    text_transformation_fx -- A function which will be applied to all text. The function must take the following parameters: the text to transform, the tag_name of the parent node
    language -- the language to use for transforming the text. This will only be used if text_transformation_fx is not none in which case the transform_text function will be used
    return_as_str -- If true, then the content will be returned as a string; otherwise a document will be returned
    allow_closing_in_start_tag -- If true, then nodes with no children will be closed without an explicit closing tag. Otherwise, they will include an explicit closing tag.
    """
    
    src_doc = parseString(xml_str)
    
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
    
    # Handle the processing node (skip it)
    elif src_node.nodeType == minidom.Node.PROCESSING_INSTRUCTION_NODE:
        pass # Don't copy processing instructions over
    
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