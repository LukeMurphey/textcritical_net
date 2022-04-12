from . import TestReader
from reader.importer.unbound_bible import UnboundBibleTextImporter
from reader.models import Author, Work, Division, Verse
from reader.importer.batch_import import JSONImportPolicy
from reader import language_tools

class TestUnboundBibleImport(TestReader):
    
    def setUp(self):
        self.importer = UnboundBibleTextImporter()
        
    def test_import_file(self):
        
        work = Work(title="LXX (Septuagint)", title_slug="lxx")
        work.save()
        
        self.importer.work = work
        
        self.importer.import_file(self.get_test_resource_file_name("lxx_a_accents_utf8.txt"))
        
        genesis   = Division.objects.filter(work=work)[0]
        chapter_1 = Division.objects.filter(work=work)[1]
        chapter_2 = Division.objects.filter(work=work)[2]
        chapter_3 = Division.objects.filter(work=work)[3]
        
        self.assertEqual(Division.objects.filter(work=work).count(), 4)
        
        self.assertEqual(Verse.objects.count(), 65)
        
        self.assertEqual(Verse.objects.filter(indicator="1")[0].content, language_tools.normalize_unicode("ἐν ἀρχῇ ἐποίησεν ὁ θεὸς τὸν οὐρανὸν καὶ τὴν γῆν"))
        self.assertEqual(Verse.objects.filter(division=chapter_1).count(), 31)
        self.assertEqual(Verse.objects.filter(division=chapter_2).count(), 25)
        self.assertEqual(Verse.objects.filter(division=chapter_3).count(), 9)
        
        self.assertEqual(genesis.title, "Genesis")
        self.assertEqual(genesis.title_slug, "genesis")
        
        # Make sure the sequence numbers increase
        num = 0
        
        for book in Division.objects.filter(readable_unit=False).order_by('sequence_number'):
            num = num + 1
            self.assertEqual(book.sequence_number, num, str(book) + " does not have the expected sequence number (%i versus expected %i)" % (book.sequence_number, num))
            
            for chapter in Division.objects.filter(parent_division=book).order_by('sequence_number'):
                num = num + 1
                self.assertEqual(chapter.sequence_number, num, str(chapter) + " does not have the expected sequence number (%i versus expected %i)" % (chapter.sequence_number, num))
        
    def test_import_file_work_not_precreated(self):
        
        self.importer.import_file(self.get_test_resource_file_name("lxx_a_accents_utf8.txt"))
        
        self.assertEqual(self.importer.work.title, "Greek OT: LXX")
        
    def test_import_file_with_policy(self):
        
        import_policy_file = self.get_test_resource_file_name("unbound_bible_import_policy.json")
        
        import_policy = JSONImportPolicy()
        import_policy.load_policy(import_policy_file)
        
        self.importer.import_policy = import_policy.should_be_processed 
        self.importer.import_file(self.get_test_resource_file_name("lxx_a_accents_utf8.txt"))
        
        self.assertEqual(self.importer.work.title, "Septuagint (LXX)")
        self.assertEqual(self.importer.work.language, "Greek")
        
    def test_load_book_names(self):
        
        book_names = self.importer.load_book_names(self.get_test_resource_file_name("book_names.txt"))
        
        self.assertEqual(book_names["01O"], "Genesis")
        
    def test_find_and_load_book_names_same_dir(self):
        
        book_names = self.importer.find_and_load_book_names(self.get_test_resource_file_name("lxx_a_accents_utf8.txt"))
        
        self.assertEqual(book_names["01O"], "Genesis")
        
    def test_find_and_load_book_names_constructor_arg(self):
        
        self.importer = UnboundBibleTextImporter(book_names_file=self.get_test_resource_file_name("book_names.txt"))
        
        book_names = self.importer.find_and_load_book_names()
        
        self.assertEqual(book_names["01O"], "Genesis")
        
    def test_get_name_from_comment(self):
        
        name = self.importer.get_name_from_comment("#name\tGreek NT: Westcott/Hort, UBS4 variants")
        
        self.assertEqual(name, "Greek NT: Westcott/Hort, UBS4 variants")
        
    def test_get_name_from_comment_truncated(self):
        
        name = self.importer.get_name_from_comment("#name\tGreek OT: LXX [A] Accented")
        
        self.assertEqual(name, "Greek OT: LXX")
