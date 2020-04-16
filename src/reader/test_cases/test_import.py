from django.test import TestCase
from reader.importer import TextImporter
from reader.models import Author
from xml.dom.minidom import parseString

class TestImport(TestCase):
     
    def setUp(self):
        self.importer = TextImporter()
        
        return super(TestImport, self).setUp()
    
    def test_make_author(self):
        
        name = "Luke Murphey"
        self.importer.make_author(name)
        self.importer.make_author(name)
        
        self.assertEquals(Author.objects.filter(name=name).count(), 1)
        
    def test_copy_node(self):
        
        src_xml = r"""
            <src>
                <vowels>
                    <a capitol="A">
                        <nocopy />
                    </a>
                </vowels>
            </src>
        """
        
        dst_xml = r"""
            <dst>
                <vowels>
                    <b capitol="B">
                    </b>
                </vowels>
            </dst>
        """
        
        src_dom = parseString(src_xml)
        dst_dom = parseString(dst_xml)
        
        # Get the nodes to copy and the place to copy them to
        node_to_copy = src_dom.getElementsByTagName("a")[0]
        to_copy_to = dst_dom.getElementsByTagName("vowels")[0]
        
        # Create the duplicate
        TextImporter.copy_node(node_to_copy, dst_dom, to_copy_to)

        expected = """<?xml version="1.0" ?><dst>
                <vowels>
                    <b capitol="B">
                    </b>
                <a capitol="A"/></vowels>
            </dst>"""
        
        self.assertEquals(expected, dst_dom.toxml())
