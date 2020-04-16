import os
from xml.dom.minidom import parseString
from . import TestReader
from reader.models import Division
from reader.importer.batch_import import ImportTransforms
from reader.importer.Perseus import PerseusTextImporter
from reader.importer.PerseusBatchImporter import PerseusBatchImporter
from reader.importer.batch_import import WorkDescriptor, wildcard_to_re, ImportPolicy

class TestPerseusBatchImporter(TestReader):
    
    def test_wildcard(self):
        
        wc_re = wildcard_to_re("*tree*")
        
        self.assertTrue(wc_re.match("pine tree") is not None)
        self.assertTrue(wc_re.match("tree bark") is not None)
        self.assertTrue(wc_re.match("pine tree bark") is not None)
        
        self.assertTrue(wc_re.match("oak") is None)
        self.assertTrue(wc_re.match("oakland") is None)
        self.assertTrue(wc_re.match("bark") is None)
        
    def test_WorkDescriptor(self):
        
        desc = WorkDescriptor(file_name="*gk.xml")
        
        self.assertFalse(desc.rejects(desc.file_name, "/Users/Luke/Downloads/test_gk.xml"))
        self.assertTrue(desc.rejects(desc.file_name, "/Users/Luke/Downloads/test_eng.xml"))
    
    def test_match_array(self):
        
        wd = WorkDescriptor(author="Lucian", title=["Abdicatus", "Anacharsis", "Bis accusatus sive tribunalia", "Cataplus"])
        
        self.assertTrue(wd.matches(["Abdicatus", "Anacharsis", "Bis accusatus sive tribunalia", "Cataplus"], "Anacharsis"))
        self.assertTrue(wd.should_be_processed("Lucian", "Anacharsis", "52.gk-xml", "Greek", None))
        
    def test_match_editor(self):
        
        wd = WorkDescriptor(editor="Herbert Weir Smyth, Ph.D.", title="Eumenides")
        
        self.assertTrue(wd.should_be_processed("Aeschylus", "Eumenides", "52.gk-xml", "Greek", "Herbert Weir Smyth, Ph.D."))
    
    def test_import(self):
        
        directory = self.get_test_resource_directory()
        
        work_descriptor = WorkDescriptor(title="Eumenides")
        
        import_policy = ImportPolicy()
        import_policy.descriptors.append(work_descriptor)
        
        importer = PerseusBatchImporter(perseus_directory=directory, book_selection_policy=import_policy.should_be_processed)
        
        self.assertEqual(importer.do_import(), 1)
        
    def test_import_editor_filter(self):
        
        directory = self.get_test_resource_directory()
        
        work_descriptor = WorkDescriptor(title="Eumenides", editor="Herbert Weir Smyth, Ph.D.")
        
        import_policy = ImportPolicy()
        import_policy.descriptors.append(work_descriptor)
        
        importer = PerseusBatchImporter(perseus_directory=directory, book_selection_policy=import_policy.should_be_processed)
        
        self.assertEqual(importer.do_import(), 1)
        
    def test_import_skip_document(self):
        
        directory = self.get_test_resource_directory()
        
        # Make sure the regular descriptor matches
        work_descriptor = WorkDescriptor(author="Plutarch", title="De primo frigido", editor=["Harold Cherniss", "William C. Helmbold"])
        
        self.assertTrue(work_descriptor.should_be_processed("Plutarch", "De primo frigido", "plut.127_loeb_eng.xml", "Greek", ["Harold Cherniss", "William C. Helmbold"]))
        
        # Make sure the dropping action matches
        work_descriptor2 = WorkDescriptor(author="Plutarch", title="De primo frigido", editor=["Harold Cherniss", "William C. Helmbold"], should_import=False)
        
        self.assertFalse(work_descriptor2.should_be_processed("Plutarch", "De primo frigido", "plut.127_loeb_eng.xml", "Greek", ["Harold Cherniss", "William C. Helmbold"]))
        
        # Now run the imports and make sure the correct action occurs when allowing importation
        import_policy = ImportPolicy()
        import_policy.descriptors.append(work_descriptor)
        
        importer = PerseusBatchImporter(perseus_directory=directory, book_selection_policy=import_policy.should_be_processed)
        
        self.assertEqual(importer.do_import(), 1)
        
        # Now run the imports and make sure the correct action occurs when dis-allowing importation
        import_policy2 = ImportPolicy()
        import_policy2.descriptors.append(work_descriptor2)
        
        importer = PerseusBatchImporter(perseus_directory=directory, book_selection_policy=import_policy2.should_be_processed)
        
        self.assertEqual(importer.do_import(), 0)
        
    def test_delete_unnecessary_divisions(self):
        
        importer = PerseusTextImporter()
        importer.state_set = 0
        importer.ignore_undeclared_divs = True
        
        book_xml = self.load_test_resource('1a_gk.xml')
        book_doc = parseString(book_xml)
        work = importer.import_xml_document(book_doc)
        
        self.assertEqual(Division.objects.filter(work=work).count(), 4)
        
        self.assertEqual(ImportTransforms.delete_unnecessary_divisions(work=work), 1)
        
        self.assertEqual(Division.objects.filter(work=work).count(), 3)
        
    def test_delete_divisions_by_title_slug(self):
        
        importer = PerseusTextImporter()
        importer.state_set = 0
        importer.ignore_undeclared_divs = True
        
        book_xml = self.load_test_resource('1a_gk.xml')
        book_doc = parseString(book_xml)
        work = importer.import_xml_document(book_doc)
        
        self.assertEqual(Division.objects.filter(work=work).count(), 4)
        
        self.assertEqual(ImportTransforms.delete_divisions_by_title_slug(work=work, title_slugs=["none"]), 1)
        
        self.assertEqual(Division.objects.filter(work=work).count(), 3)
