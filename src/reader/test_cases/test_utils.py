from . import TestReader
from reader.utils import remove_unnecessary_whitespace

class TestUtilsRemoveWhitespace(TestReader):
    
    def test_strip_edges(self):
        self.assertEqual(remove_unnecessary_whitespace('    1  '), '1')

    def test_strip_too_many_endlines(self):
        self.assertEqual(remove_unnecessary_whitespace('1\n\n2', False), '1\n2')

    def test_strip_too_many_spaces(self):
        self.assertEqual(remove_unnecessary_whitespace('1  2'), '1 2')

    def test_strip_too_many_endlines_and_spaces(self):
        self.assertEqual(remove_unnecessary_whitespace('1 \n\n\n     2', False), '1 \n 2')
    
    def test_strip_all_endlines(self):
        self.assertEqual(remove_unnecessary_whitespace('1 \n\n\n     2', True), '1 2')
