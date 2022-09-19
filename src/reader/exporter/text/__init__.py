from reader.templatetags.reader_extras import transform_perseus_text, transform_perseus_node, convert_xml_to_html5, NoteNumber
from reader.exporter.text_conversion.text_converter import TextConverter
from collections import OrderedDict

def convert_verses_to_text(verses, chapter):
    # Initialize the output
    txt_output = ''
    note_number = NoteNumber(1)
    notes = OrderedDict()
    verses_exported = 0
    
    # Output each verse
    for verse in verses:
        # Add some padding between the verses.
        if verses_exported > 0:
            txt_output += " "
        
        # Add the verse indicator
        if len(verse.indicator) > 0:
            txt_output += verse.indicator + '. '
            
        # Use the original content if it exists
        if len(verse.original_content) > 0:
            verse_txt, new_notes = convert_verse_to_text(verse.original_content, chapter.work.language, note_number)
            
            txt_output += verse_txt
            
            # Incorporate the new notes
            notes.update(new_notes)
            note_number = NoteNumber(len(notes) + 1)
            
        # Otherwise, use the original content
        else:
            txt_output += verse.content

        verses_exported += 1
        
    # Add the footnotes
    if len(notes) > 0:
        txt_output += "\n\nFootnotes:"
        
        for note_number, note_text in notes.items():
            txt_output += "\n[{}] {}".format(note_number, note_text)
    
    return txt_output
        
def convert_verse_to_text(xml_str, language, note_number):
    text_transformation_fx = lambda text, parent_node, dst_doc: transform_perseus_text(text, parent_node, dst_doc, language, disable_wrapping=True)
    node_transformation_fx = lambda tag, attrs, parent, dst_doc: transform_perseus_node(tag, attrs, parent, dst_doc, True, False, note_number, note_prefix=None)
    
    converted_doc = convert_xml_to_html5(xml_str, return_as_str=True, text_transformation_fx=text_transformation_fx, language=language, node_transformation_fx=node_transformation_fx)

    # Convert the document to text
    # We will do this by extracting the text portions but a little special handling of the footnotes
    converter = TextConverter(int(note_number.value()))
    converter.feed(converted_doc)
    extracted_txt = converter.text_doc
    
    # Output the content
    return extracted_txt.strip(), converter.notes