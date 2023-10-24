from reader.templatetags.reader_extras import NoteNumber
from collections import OrderedDict
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from reader.exporter.text import convert_verse_to_text

def convert_verses_to_text(verses, chapter):

    # Initialize the output
    document = Document()
    note_number = NoteNumber(1)
    notes = OrderedDict()
    verses_exported = 0
    
    # Declare the meta-data
    document.core_properties.title = chapter.work.title + "; " + " ".join(chapter.get_division_titles())
    document.core_properties.comments = "Downloaded from TextCritical.net"
    document.core_properties.language = chapter.work.language

    # Get a reference to the style used for the verse markers
    # A separate style is used so that you can hide the markers by using setting the 'hidden'
    # font attribute.
    verse_marker_style = document.styles.add_style('Verse Marker', WD_STYLE_TYPE.CHARACTER)
    verse_marker_style.base_style = document.styles['Strong']
    verse_marker_style.hidden = False
    verse_marker_style.quick_style = True
     
    # Output the header
    document.add_paragraph(" ".join(chapter.get_division_titles())).style = document.styles['Heading 1']
    
    p = document.add_paragraph()
    
    # Output each verse
    for verse in verses:
        # Add some padding between the verses.
        if verses_exported > 0:
            p.add_run(' ')
        
        # Add the verse indicator
        if len(verse.indicator) > 0:
            p.add_run(verse.indicator + '. ').style = verse_marker_style
            
        # Use the original content if it exists
        if len(verse.original_content) > 0:
            verse_txt, new_notes = convert_verse_to_text(verse.original_content, chapter.work.language, note_number)

            p.add_run(verse_txt)
            
            # Incorporate the new notes
            notes.update(new_notes)
            note_number = NoteNumber(len(notes) + 1)
            
        # Otherwise, use the original content
        else:
            p.add_run(verse.content)

        verses_exported += 1
        
    # Add the footnotes
    if len(notes) > 0:
        document.add_page_break()
        document.add_heading('Footnotes:', level=1)
        
        for note_number, note_text in notes.items():
            p = document.add_paragraph("[{}] {}".format(note_number, note_text))
    
    return document
