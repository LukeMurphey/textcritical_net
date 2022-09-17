from six.moves.html_parser import HTMLParser

class TextConverter(HTMLParser):
    """
    Takes an XML document and produces a text version.
    """
    
    def __init__(self):
        """
        Initialize the text converter.
        """
        
        self.text_doc = ''

        # initialize the base class
        HTMLParser.__init__(self)
    
    def handle_data(self, data):
        self.text_doc = self.text_doc + data
