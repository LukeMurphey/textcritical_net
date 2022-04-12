from xml.dom.minidom import parseString
from . import TestReader
from reader.importer.Perseus import PerseusTextImporter
from reader.utils.work_helpers import get_work_page_info
from reader.models import WorkAlias

class TestWorkHelpers(TestReader):
    
    def setUp(self):
        self.importer = PerseusTextImporter()
    
    def test_get_work_page_info(self):
        # Import a work for us to use
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)

        WorkAlias.populate_alias_from_work(self.importer.work)

        # Get the work information
        data = get_work_page_info(title=self.importer.work.title_slug, division_0=1)

        self.assertEqual(data['title'], 'Josephi vita 1')
