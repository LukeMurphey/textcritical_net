import xml.dom.minidom as minidom
from reader.language_tools.greek import Greek
from reader.language_tools import transform_text

from HTMLParser import HTMLParser
from xml.dom.minidom import parseString
from htmlentitydefs import name2codepoint
from time import time

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page

import logging

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
        text_transformation_fx -- A function which will be applied to all text. The function must take the following parameters: the text to transform, the tag_name of the parent node, document
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
            
            # Transform the text
            transformed_text = self.text_transformation_fx( text=data, parent_node=self.current_node, dst_doc=self.dst_doc )
            
            # Don't bother appending empty text
            if transformed_text is not None:
                txt_node = self.dst_doc.createTextNode( transformed_text.decode( "utf-8" ) )
            else:
                txt_node = None
            
        else:
            txt_node = self.dst_doc.createTextNode( data )

        # Append the txt node
        if txt_node:
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
        text_transformation_fx = lambda text, parent_node, dst_doc: transform_text(text, language)
    
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
        
logger = logging.getLogger(__name__)
        
def time_function_call(fx):
    """
    This decorator will provide a log message measuring how long a function call took.
    
    Arguments:
    fx -- The function to measure
    """
    
    def wrapper(*args, **kwargs):
        t = time()
        
        r = fx(*args, **kwargs)
        
        diff = time() - t
        
        diff_string = str( round( diff, 6) ) + " seconds"
        
        logger.debug( "%s, duration=%s", fx.__name__, diff_string )
        
        return r
    return wrapper

def uniquefy(seq, idfun=None):
    
    # order preserving
    if idfun is None:
        def idfun(x): return x
         
    seen = {}
    result = []
   
    for item in seq:
        
        marker = idfun(item)
        
        if marker in seen: continue
        
        seen[marker] = 1
        result.append(item)
        
    return result

def string_limiter(text, limit):
    """
    Reduces the number of words in the string to length provided.
    
    Arguments:
    text -- The string to reduce the length of
    limit -- The number of characters that are allowed in the string
    """
    
    for i in range(len(text)):
        
        if i >= limit and text[i] == " ":
            break
    
    return text[:i]

def ajaxify(fn):
    """
    Loads a page that inserts an AJAX request to load the content in another request so that the page can be loaded quickly.
    """
    
    def ajax_switch(*args, **kwargs):
        
        # Get the request (which ought to be the first argument)
        request = args[0]
        
        # If the call is not a GET, then just pass it through
        if request.method != "GET":
            return fn(*args, **kwargs)
        
        # If we are told to treat the request as synchronous, then just pass it through
        if 'async' in request.GET and request.GET['async'] == "0":
            return fn(*args, **kwargs)
        
        # If the call is an AJAX call, then pass it through
        if request.is_ajax():
            return fn(*args, **kwargs)
        
        # If the call is a plain GET call, then get it
        return render_to_response('ajah_redirect.html',
                                  {'content_url' : request.get_full_path() },
                                  context_instance=RequestContext(request))
    
    return ajax_switch

class cache_page_if_ajax(object):
    """
    Provides a decorator that facilitates caching only if the response is an AJAX response. This is useful when the content of the page is different based
    on whether it is an AJAX request (includes the "HTTP_X_REQUESTED_WITH" set to "XMLHttpRequest"). This is necessary for pages that call themselves to after
    loading in order to get the page content but setup the call to be a AJAX request by setting the appropriate header. In this case, only the AJAX response
    ought to be cached, not the outermost call.
    """
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self, fn):
        
        def return_cached_page_if_ajax(*args, **kwargs):
            
            request = args[0]
            
            if request.is_ajax():
                # See https://github.com/django/django/blob/master/django/views/decorators/cache.py
                return cache_page(fn, *self.args, **self.kwargs)(*args, **kwargs)
                
            else:
                return fn(*args, **kwargs)
            
        return return_cached_page_if_ajax
        