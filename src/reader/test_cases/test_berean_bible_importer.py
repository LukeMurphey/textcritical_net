import os

from . import TestReader
from reader.importer.berean_bible import BereanBibleImporter
from reader.models import Work, Division, Verse
from reader.importer.batch_import import JSONImportPolicy

class TestBereanBibleImport(TestReader):

    def test_parse_line(self):
        book, chapter, verse, text = BereanBibleImporter.parse_line("2 Thessalonians 3:9	Not that we lack this right, but we wanted to offer ourselves as an example for you to imitate.")

        self.assertEqual(book, "2 Thessalonians")
        self.assertEqual(chapter, "3")
        self.assertEqual(verse, "9")
        self.assertEqual(text, "Not that we lack this right, but we wanted to offer ourselves as an example for you to imitate.")

    def test_parse_line_large_chapter_num(self):
        book, chapter, verse, text = BereanBibleImporter.parse_line("Genesis 43:17	The man did as Joseph had commanded and took the brothers to Joseph's house.")

        self.assertEqual(book, "Genesis")
        self.assertEqual(chapter, "43")
        self.assertEqual(verse, "17")
        self.assertEqual(text, "The man did as Joseph had commanded and took the brothers to Joseph's house.")

    def test_parse_line_invalid(self):
        line = "The Holy Bible, Berean Bible, Copyright ©2016-2020 by Bible Hub. All Rights Reserved Worldwide.	"
        book, chapter, verse, text = BereanBibleImporter.parse_line(line)

        self.assertEqual(book, None)
        self.assertEqual(chapter, None)
        self.assertEqual(verse, None)
        self.assertEqual(text, line)

    def test_import(self):
        # Make the base work
        work = Work(title="Berean Study Bible", title_slug="bsb")
        work.save()

        Work(title_slug="asv").save()
        Work(title_slug="lxx").save()
        Work(title_slug="new-testament").save()

        # Get the path to the import policy accounting for the fact that the command may be run outside of the path where manage.py resides
        import_policy_file = os.path.join("reader", "importer", "berean_bible_import_policy.json")
        
        import_policy = JSONImportPolicy()
        import_policy.load_policy(import_policy_file)

        # Make sure the policy got loaded
        self.assertEqual(len(import_policy.descriptors), 1)

        importer = BereanBibleImporter(work=work, import_policy=import_policy.should_be_processed)
        importer.import_file(self.get_test_resource_file_name("bsb.txt"))

        # Verify the division count
        self.assertEqual(len(Division.objects.filter(work=work)), 9)

        # Verify the books (3)
        self.assertEqual(len(Division.objects.filter(work=work, level=1)), 4)

        # Verify the chapters (4)
        self.assertEqual(len(Division.objects.filter(work=work, readable_unit=True)), 5)

        # Verify the verses
        genesis = Division.objects.filter(work=work, level=1, descriptor="Genesis")[0]
        self.assertEqual(genesis.descriptor, 'Genesis')

        # Get chapter 1 of Genesis
        genesis_1 = Division.objects.filter(work=work, parent_division=genesis, level=2, descriptor="1")[0]
        self.assertEqual(genesis_1.descriptor, '1')
        self.assertEqual(genesis_1.sequence_number, 2)
        self.assertEqual(genesis_1.get_division_description(), 'Genesis 1')
        self.assertEqual(genesis_1.get_division_description_titles(), 'Genesis Chapter 1')

        # Get the verses of Genesis 1
        genesis_verses = Verse.objects.filter(division=genesis_1)
        self.assertEqual(len(genesis_verses), 5)

        self.assertEqual(genesis_verses[0].content, 'In the beginning God created the heavens and the earth.')
        # https://lukemurphey.net/issues/2616
        self.assertEqual(genesis_verses[2].content, 'And God said, “Let there be light,” and there was light.')

        # Make sure that import policy worked
        updated_work = Work.objects.get(title_slug=work.title_slug)

        psalm = Division.objects.filter(work=work, level=1, descriptor="Psalms")[0]
        self.assertEqual(psalm.title, 'Psalms')
