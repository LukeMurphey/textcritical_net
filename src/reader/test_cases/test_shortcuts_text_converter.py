from . import TestReader
from reader.shortcuts.perseus_notes import PerseusNotesExtractor
from reader.models import Division
from reader.shortcuts.text_converter import TextConverter

class TestShortcutsTextConverter(TestReader):
    def test_drop_notes(self):
        xml = """<div>
<span id="verse-" class="verse-container">
    <span class="verse">
       <i class="icon-info-sign icon-white note-tag" id="80f31868"></i>
       <span class="label note hide" id="content_for_80f31868">CONCERNING ABIMELECH; AND CONCERNING ISMAEL THE SON OF ABRAHAM;
             AND CONCERNING THE ARABIANS, WHO WERE HIS POSTERITY.
       </span>
    </span>
</span>

<span id="verse-1" class="verse-container">
    <a class="verse-link" href="/work/antiquities-of-the-jews/1/12/1" data-verse="1" data-verse-descriptor="1.12.1" data-original-id="verse-link_1" id="verse-link_1">
        <span class="label verse number">1</span>
    </a>
    
    <span class="verse">
    <span class="p">ABRAHAM now removed to Gerar</span>
    of Palestine, leading Sarah along with
him, under the notion of his sister, using the like dissimulation that
he had used before, and this out of fear: for he was afraid of Abimelech,
    </span>
</span>
</div>"""

        importer = TextConverter(include_notes_at_end=True)
        importer.feed(xml)

        # self.assertFalse("CONCERNING ABIMELECH" in importer.text_doc)
        self.assertTrue("Footnotes:" in importer.text_doc)
        self.assertTrue("[1] CONCERNING ABIMELECH; AND CONCERNING ISMAEL THE SON OF ABRAHAM;" in importer.text_doc)
        
    def test_drop_notes_2(self):
        xml = """<div>
Luke Murphey is a software developer<span class="label note hide">See https://lukemurphey.net</span> who has worked for various companies and currently works for Splunk<span class="label note hide">See https://splunk.com</span> which is a Big Data software company.
</div>"""

        importer = TextConverter(include_notes_at_end=True)
        importer.feed(xml)

        self.assertTrue("Footnotes:" in importer.text_doc)
        self.assertTrue("[1] See https://lukemurphey.net" in importer.text_doc)
        self.assertTrue("[2] See https://splunk.com" in importer.text_doc)
        
        self.assertTrue("Luke Murphey is a software developer[1] who has worked for various companies" in importer.text_doc)
        self.assertTrue("currently works for Splunk[2] which is a Big Data software company" in importer.text_doc)