from tempfile import NamedTemporaryFile

from . import TestReader
from reader.ebook import ePubExport
from reader.models import Division, Work, Verse
from reader.importer.Perseus import PerseusTextImporter

class TestEpubExport(TestReader):
    
    def test_get_perseus_notes(self):
        
        #book_xml = self.load_test_resource('aesch.ag_eng.xml')
        s = """<div1 type="episode">For the rest I stay silent;
        a great ox stands upon my tongue<note anchored="yes" n="36" resp="Smyth">A proverbial expression &lpar;of uncertain origin&rpar; for enforced silence; cf. fr. 176, &ldquo;A key stands guard upon my tongue.&rdquo;</note>
        </div1>"""
  
        #book_doc = parseString(book_xml)
        
        work = Work()
        work.language = "english"
        
        division = Division()
        division.work = work
        division.original_content = s
        
        #division_map = ePubExport.DivisionMap(division, None)
        
        notes = ePubExport.getPerseusNotesFromDivisionContent(division)
        
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].text, 'A proverbial expression (of uncertain origin) for enforced silence; cf. fr. 176, “A key stands guard upon my tongue.”')

    def test_get_perseus_notes_from_verses_not_ignoring_notes(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('aesch.ag_eng.xml')

        importer = PerseusTextImporter(ignore_notes=False)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = ePubExport.getPerseusNotesFromVerses(divisions[1])

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].text, 'A proverbial expression of uncertain origin for enforced silence; cf. fr. 176, A key stands guard upon my tongue.')

    def test_get_perseus_notes_from_verses_ignoring_notes(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('aesch.ag_eng.xml')

        importer = PerseusTextImporter(ignore_notes=True)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = ePubExport.getPerseusNotesFromVerses(divisions[1])

        self.assertEqual(len(notes), 0)

    def test_get_perseus_notes_from_verses_ignoring_notes_subdivisions(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('hist_eng.xml')

        importer = PerseusTextImporter(ignore_notes=True)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = ePubExport.getPerseusNotesFromVerses(divisions[1])

        self.assertEqual(len(notes), 0)

    def test_get_perseus_notes_from_verses_not_ignoring_notes_subdivisions(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('hist_eng.xml')

        importer = PerseusTextImporter(ignore_notes=False)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = ePubExport.getPerseusNotesFromVerses(divisions[0])

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].text, 'Introduction. The importance and magnitude of the subject.')
        
    def test_split_text_into_lines(self):
        
        lines = ePubExport.splitTextIntoMultipleLines("Antiquities of the Jews", 12)
        self.assertEqual(lines, "Antiquities\nof the Jews")
        
        lines = ePubExport.splitTextIntoMultipleLines("The Extant Works of Aretaeus, The Cappadocian", 24)
        self.assertEqual(lines, "The Extant Works of\nAretaeus, The Cappadocian")
        
        lines = ePubExport.splitTextIntoMultipleLines("Alcibiades 1, Alcibiades 2, Hipparchus, Lovers, Theages, Charmides, Laches, Lysis", 24)
        self.assertEqual(lines, "Alcibiades 1, Alcibiades\n2, Hipparchus, Lovers,\nTheages, Charmides,\nLaches, Lysis")

    def test_export_work(self):
        # Make a work
        work = Work()
        work.title = 'test case'
        work.language = "english"
        work.save()
        
        division = Division()
        division.work = work
        division.sequence_number = 1
        division.level = 1
        division.save()

        content = ' some content goes here'
        verse = Verse(division=division, indicator="1", sequence_number=1, content=content)
        verse.save()

        # Make the place to export the file
        epub_file = NamedTemporaryFile(delete=False)
        epub_file.close()

        # Export it
        ePubExport.exportWork(work, epub_file.name)

    def test_export_perseus_work(self):
        # Import a Perseus work
        file_name = self.get_test_resource_file_name('hist_eng.xml')

        importer = PerseusTextImporter(ignore_notes=False)
        importer.import_file(file_name)

        # Make the place to export the file
        epub_file = NamedTemporaryFile(delete=False)
        epub_file.close()

        # Export it
        ePubExport.exportWork(importer.work, epub_file.name)
    