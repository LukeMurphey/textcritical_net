from xml.dom.minidom import parseString
from . import TestReader
from reader.importer.Perseus import PerseusTextImporter
from reader.models import Division, Verse
from reader.importer.batch_import import ImportTransforms
from reader.importer.Lexicon import LexiconImporter

class TestPerseusImportLexicon(TestReader):
    """
    # See #2322, https://lukemurphey.net/issues/2322
    """

    def setUp(self):
        self.importer = PerseusTextImporter(division_tags=["entry", "div0"])

    def test_load_lexicon(self):
        book_xml = self.load_test_resource('ml.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEqual(len(Verse.objects.filter(division=divisions[1])), 1) # Should have 9 entries for the letter alpha
        self.assertEqual(divisions.count(), 15) # Should have two divisions for the letters and 13 for the entries

        # Make sure that the division description got converted from beta-code
        self.assertEqual(divisions[0].title, '\u0391') # Should be Α
        self.assertEqual(str(divisions[0]), "Α") # Should be Α
        #self.assertEqual(divisions[0].title_slug, "a") # Should be Α
        self.assertEqual(divisions[0].descriptor, "*a")
        self.assertEqual(divisions[1].descriptor, "ἀάατος")

        #self.assertEqual(str(divisions[1]), "ἀάατος")

        # Update the descriptors
        ImportTransforms.convert_descriptors_from_beta_code(self.importer.work)
        self.assertEqual(divisions[0].descriptor, '\u0391')
        
        # Ensure that the division has a valid readable string
        # See https://lukemurphey.net/issues/2355
        self.assertEqual(str(divisions[1]), "main ἈΆΑΤΟΣ")
        self.assertEqual(divisions[1].get_division_description(use_titles=False), 'Α ἈΆΑΤΟΣ')
        

    def test_find_entries(self):
        book_xml = self.load_test_resource('ml.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)

        divisions = Division.objects.filter(work=self.importer.work)
        verses = Verse.objects.filter(division=divisions[1])

        verse = verses[:1][0]

        entries = LexiconImporter.find_perseus_entries(verse)
        
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], "a)a/atos")
