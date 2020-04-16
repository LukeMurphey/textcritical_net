from . import TestReader
from reader.models import Division, Verse
from reader.importer.Perseus import PerseusTextImporter

class TestDivisionModel(TestReader):
    
    def setUp(self):
        self.importer = PerseusTextImporter()
    
    def test_get_division_indicators(self):
        
        book_xml = self.load_test_resource('nt_gk.xml')        
        self.importer.import_xml_string(book_xml)
        
        division = Division.objects.filter(work=self.importer.work)[1]
        
        self.assertEquals(division.get_division_indicators(), ['Matthew', '1'])
        
    def test_get_division_description(self):
        
        book_xml = self.load_test_resource('nt_gk.xml')        
        self.importer.import_xml_string(book_xml)
        
        # Build a description
        division = Division.objects.filter(work=self.importer.work)[1]
        self.assertEquals(division.get_division_description(), "Matthew 1")
        
        # Build a description using the titles
        division = Division.objects.filter(work=self.importer.work)[1]
        self.assertEquals(division.get_division_description(use_titles=True), "ΚΑΤΑ ΜΑΘΘΑΙΟΝ chapter 1")
        
        # Build a description with a verse
        verse = Verse.objects.filter(division=division).order_by("sequence_number")[0]
        self.assertEquals(division.get_division_description(verse=verse), "Matthew 1:1")
    