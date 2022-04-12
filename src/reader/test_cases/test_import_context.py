from django.test import TestCase
from reader.importer import TextImporter

class TestImportContext(TestCase):
        
    def test_division_level(self):
        context = TextImporter.ImportContext("TestCase")
        
        self.assertEqual(context.get_division_level_count(2), 0)
        
        context.increment_division_level(2)
        self.assertEqual(context.get_division_level_count(2), 1)
