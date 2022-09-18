from reader.models import Division, Verse
from reader.templatetags.reader_extras import transform_perseus_text, transform_perseus_node
from reader.shortcuts import convert_xml_to_html5
import xml.dom.minidom

class PerseusNotesExtractor(object):
    class Note(object):
        
        def __init__(self, text, division):
            self.text = text
            self.division = division
    
    @classmethod
    def getText(cls, node):
        
        if node.nodeType == xml.dom.minidom.Element.TEXT_NODE:
            text = node.data
        else:
            text = ""
        
        for n in node.childNodes:
            text = text + cls.getText(n)
                
        return text
    
    @classmethod
    def getPerseusNotesFromVerses(cls, division):
        
        language = division.work.language
        
        # Make the function to perform the transformation
        text_transformation_fx = lambda text, parent_node, dst_doc: transform_perseus_text(text, parent_node, dst_doc, language)

        transform_perseus_node_epub = lambda tag, attrs, parent, dst_doc: transform_perseus_node(tag, attrs, parent, dst_doc, True, True)

        notes = []

        # Get the notes from the sub-divisions
        for subdivision in Division.objects.filter(parent_division=division):
            notes.extend(cls.getPerseusNotesFromVerses(subdivision))

        # Get the notes from the verses
        for verse in Verse.objects.filter(division=division):
            converted_doc = convert_xml_to_html5(verse.original_content, language=language, text_transformation_fx=text_transformation_fx, node_transformation_fx=transform_perseus_node_epub )
            nodes = converted_doc.getElementsByTagName("span")

            for node in nodes:
                
                if node.attributes.get('class', None) != None:
                    classes = node.attributes.get('class', None).value.split(" ")
                
                    if "note" in classes:
                        
                        text = cls.getText(node)
                        
                        note = cls.Note(text, division)
                        notes.append(note)

        return notes
    
    @classmethod
    def getPerseusNotesFromDivisionContent(cls, division):
        
        language = division.work.language
        
        # Make the function to perform the transformation
        text_transformation_fx = lambda text, parent_node, dst_doc: transform_perseus_text(text, parent_node, dst_doc, language)
        
        transform_perseus_node_epub = lambda tag, attrs, parent, dst_doc: transform_perseus_node(tag, attrs, parent, dst_doc, True, True)
    
        converted_doc = convert_xml_to_html5(division.original_content, language=language, text_transformation_fx=text_transformation_fx, node_transformation_fx=transform_perseus_node_epub )
        nodes = converted_doc.getElementsByTagName("span")
        notes = []
        
        for node in nodes:
            
            if node.attributes.get('class', None) != None:
                classes = node.attributes.get('class', None).value.split(" ")
            
                if "note" in classes:
                    
                    text = cls.getText(node)
                    
                    note = cls.Note(text, division)
                    notes.append(note)
        
        return notes
