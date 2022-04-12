from django.test import TestCase
from reader.importer import LineNumber

class TestLineNumber(TestCase):
    
    def test_parse(self):
        line_number = LineNumber()
        line_number.set("354a")
        
        self.assertEqual(line_number.post, "a")
        self.assertEqual(line_number.number, 354)
        self.assertEqual(str(line_number), "354a")
    
    def test_increment(self):
        line_number = LineNumber()
        line_number.set("354a")
        line_number.increment()
        
        self.assertEqual(line_number.number, 355)
        self.assertEqual(str(line_number), "355a")
        
    def test_copy(self):
        line_number = LineNumber()
        line_number.set("354a")
        
        new_line_number = line_number.copy()
        
        line_number.pre = "_"
        
        self.assertEqual(str(new_line_number), "354a")
        
    def test_str(self):
        
        line_number = LineNumber()
        line_number.set("354a")
        
        self.assertEqual(str(line_number), "354a")
