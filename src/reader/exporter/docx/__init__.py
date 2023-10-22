from reader.templatetags.reader_extras import NoteNumber
from collections import OrderedDict
from docx import Document
from reader.exporter.text import convert_verse_to_text

def convert_verses_to_text(verses, chapter):

    # Initialize the output
    document = Document()
    note_number = NoteNumber(1)
    notes = OrderedDict()
    verses_exported = 0

    # Get a reference to the strong style (used for the verse markers)
    strong_style = document.styles['Strong']
     
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
            p.add_run(verse.indicator + '. ').style = strong_style
            
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
