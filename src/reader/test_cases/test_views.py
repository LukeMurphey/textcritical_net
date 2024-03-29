from . import TestReader
from reader.models import Division, Verse
from reader.importer.Perseus import PerseusTextImporter
from reader.utils.work_helpers import get_division, convert_to_numbered_division_name, convert_to_lettered_division_name, has_lettered_book_number, has_numbered_book_number

class TestViews(TestReader):
    
    def test_get_division(self):
        
        importer = PerseusTextImporter()
        book_xml = self.load_test_resource('nt_gk.xml')
        work = importer.import_xml_string(book_xml)
        
        division = get_division(work, 'Matthew', '1')
        
        self.assertEqual(division.descriptor, '1')
        self.assertEqual(division.parent_division.descriptor, 'Matthew')
    
    def test_convert_to_numbered_division_name(self):
        self.assertEqual(convert_to_numbered_division_name("I Timothy"), '1 Timothy')
        self.assertEqual(convert_to_numbered_division_name("II Timothy"), '2 Timothy')
        self.assertEqual(convert_to_numbered_division_name("I Corinthians"), '1 Corinthians')
        self.assertEqual(convert_to_numbered_division_name("III John"), '3 John')
        self.assertEqual(convert_to_numbered_division_name("VII John"), 'VII John')
        self.assertEqual(convert_to_numbered_division_name("Mark"), 'Mark')
    
    def test_convert_to_lettered_division_name(self):
        self.assertEqual(convert_to_lettered_division_name("1 Timothy"), 'I Timothy')
        self.assertEqual(convert_to_lettered_division_name("2 Timothy"), 'II Timothy')
        self.assertEqual(convert_to_lettered_division_name("3 John"), 'III John')
        self.assertEqual(convert_to_numbered_division_name("9 John"), '9 John')
        self.assertEqual(convert_to_lettered_division_name("Mark"), 'Mark')
        
    def test_has_lettered_book_number(self):
        self.assertEqual(has_lettered_book_number("I Timothy"), True)
        self.assertEqual(has_lettered_book_number("II Timothy"), True)
        self.assertEqual(has_lettered_book_number("I Corinthians"), True)
        self.assertEqual(has_lettered_book_number("III John"), True)
        self.assertEqual(has_lettered_book_number("Mark"), False)
    
    def test_has_numbered_book_number(self):
        self.assertEqual(has_numbered_book_number("1 Timothy"), True)
        self.assertEqual(has_numbered_book_number("2 Timothy"), True)
        self.assertEqual(has_numbered_book_number("3 John"), True)
        self.assertEqual(has_numbered_book_number("Mark"), False)
