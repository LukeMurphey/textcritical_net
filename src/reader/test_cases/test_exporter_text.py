from . import TestReader
from reader.importer.unbound_bible import UnboundBibleTextImporter
from reader.models import Author, Work, Division, Verse
from reader.importer.batch_import import JSONImportPolicy
from reader import language_tools
from reader.exporter.text import convert_verses_to_text

class TestTextExporter(TestReader):
    def test_export_with_footnote(self):
        # Make a work
        work = Work()
        work.title = 'test case'
        work.language = "greek"
        work.save()
        
        division = Division()
        division.work = work
        division.sequence_number = 1
        division.level = 1
        division.save()

        content = """<?xml version="1.0" ?>
        <verse>
            <p>
            th=s po/lews,<note anchored="yes" resp="Loeb"><foreign lang="greek"> oi( th=s po/lews </foreign> H. Wolf :
            <foreign lang="greek">  peri\ th=s po/lews </foreign> MSS.</note> pa/lin de\ meta\ tou=to a)nteceta/sai
            </p>
        </verse>"""

        verse = Verse(division=division, indicator="1", sequence_number=1, original_content=content)
        verse.save()
        
        txt = convert_verses_to_text(Verse.objects.filter(division=division), division)

        self.assertTrue("1. τῆς πόλεως,[1] πάλιν δὲ μετὰ τοῦτο ἀντεξετάσαι" in txt)
        self.assertTrue("Footnotes:\n[1]  οἱ τῆς πόλεως" in txt)
        
    def test_export_with_multiple_footnotes(self):
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

        content = """<?xml version="1.0" ?>
        <verse>
            <p>
            Luke Murphey<note>https://LukeMurphey.net</note> wrote TextCritical<note>https://TextCritical.net</note>
            starting in 2012 after struggling to find cheap or free copies of ancient Greek works.
            </p>
        </verse>"""

        verse = Verse(division=division, indicator="1", sequence_number=1, original_content=content)
        verse.save()
        
        txt = convert_verses_to_text(Verse.objects.filter(division=division), division)

        expected = """1. Luke Murphey[1] wrote TextCritical[2]
            starting in 2012 after struggling to find cheap or free copies of ancient Greek works.

Footnotes:
[1] https://LukeMurphey.net
[2] https://TextCritical.net"""

        self.assertEqual(expected, txt)
        
    def test_export_with_multiple_footnotes_and_verses(self):
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

        content = """<?xml version="1.0" ?>
        <verse>
            <p>
            Luke Murphey<note>https://LukeMurphey.net</note> wrote TextCritical<note>https://TextCritical.net</note>
            </p>
        </verse>"""

        verse = Verse(division=division, indicator="1", sequence_number=1, original_content=content)
        verse.save()
        
        content2 = """<?xml version="1.0" ?>
        <verse>
            <p>
            The sourcecode is hosted on Git<note>https://github.com/LukeMurphey/textcritical_net</note>
            </p>
        </verse>"""
        
        verse2 = Verse(division=division, indicator="2", sequence_number=1, original_content=content2)
        verse2.save()
        
        txt = convert_verses_to_text(Verse.objects.filter(division=division), division)

        expected = """1. Luke Murphey[1] wrote TextCritical[2] 2. The sourcecode is hosted on Git[3]

Footnotes:
[1] https://LukeMurphey.net
[2] https://TextCritical.net
[3] https://github.com/LukeMurphey/textcritical_net"""

        self.assertEqual(expected, txt)