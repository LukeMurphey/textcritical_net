from . import TestReader
from reader.shortcuts import convert_xml_to_html5, convert_xml_to_text
from reader.templatetags.reader_extras import perseus_xml_to_html5
from . import TestReader
from reader.shortcuts.perseus_notes import PerseusNotesExtractor
from reader.models import Division, Work
from reader.importer.Perseus import PerseusTextImporter

class TestShortcutsPerseusNotes(TestReader):
    
    def test_get_perseus_notes(self):
        s = """<div1 type="episode">For the rest I stay silent;
        a great ox stands upon my tongue<note anchored="yes" n="36" resp="Smyth">A proverbial expression &lpar;of uncertain origin&rpar; for enforced silence; cf. fr. 176, &ldquo;A key stands guard upon my tongue.&rdquo;</note>
        </div1>"""
        
        work = Work()
        work.language = "english"
        
        division = Division()
        division.work = work
        division.original_content = s
        
        notes = PerseusNotesExtractor.getPerseusNotesFromDivisionContent(division)
        
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].text, 'A proverbial expression (of uncertain origin) for enforced silence; cf. fr. 176, “A key stands guard upon my tongue.”')

    def test_get_perseus_notes_from_verses_not_ignoring_notes(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('aesch.ag_eng.xml')

        importer = PerseusTextImporter(ignore_notes=False)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = PerseusNotesExtractor.getPerseusNotesFromVerses(divisions[1])

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].text, 'A proverbial expression of uncertain origin for enforced silence; cf. fr. 176, A key stands guard upon my tongue.')

    def test_get_perseus_notes_from_verses_ignoring_notes(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('aesch.ag_eng.xml')

        importer = PerseusTextImporter(ignore_notes=True)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = PerseusNotesExtractor.getPerseusNotesFromVerses(divisions[1])

        self.assertEqual(len(notes), 0)

    def test_get_perseus_notes_from_verses_ignoring_notes_subdivisions(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('hist_eng.xml')

        importer = PerseusTextImporter(ignore_notes=True)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = PerseusNotesExtractor.getPerseusNotesFromVerses(divisions[1])

        self.assertEqual(len(notes), 0)

    def test_get_perseus_notes_from_verses_not_ignoring_notes_subdivisions(self):
        # See issue #2006 (https://lukemurphey.net/issues/2006)
        file_name = self.get_test_resource_file_name('hist_eng.xml')

        importer = PerseusTextImporter(ignore_notes=False)
        importer.import_file(file_name)

        divisions = Division.objects.filter(work=importer.work).order_by("sequence_number")
        
        notes = PerseusNotesExtractor.getPerseusNotesFromVerses(divisions[0])

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].text, 'Introduction. The importance and magnitude of the subject.')
    