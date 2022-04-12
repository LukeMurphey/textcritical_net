from . import TestReader, time_function_call
from reader import utils
from reader.importer.Diogenes import DiogenesLemmataImporter, DiogenesAnalysesImporter
from reader import language_tools

class TestReaderUtils(TestReader):

    def setUp(self):
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
    @time_function_call
    def test_get_word_descriptions(self):
        descriptions = utils.get_word_descriptions("ἅβρυνα", False)
        
        self.assertEqual(len(descriptions), 2)

    @time_function_call
    def test_get_lemma(self):
        lemma = utils.get_lemma(language_tools.greek.Greek.beta_code_to_unicode("a(/rpina"))
        self.assertNotEqual(lemma, None)

        lemma = utils.get_lemma("ἅρπινα", False)
        self.assertNotEqual(lemma, None)

        lemma = utils.get_lemma("αρπινα", True)
        self.assertNotEqual(lemma, None)

    @time_function_call
    def test_get_lemma_no_diacritics(self):
        lemma = utils.get_lemma("αρπινα", True)
        
        self.assertNotEqual(lemma, None)
        
    @time_function_call
    def test_get_all_related_forms(self):
        forms = utils.get_all_related_forms("ἅβραν", False) #a(/bran
        
        self.assertEqual(len(forms), 6)
        
    @time_function_call
    def test_get_all_related_forms_no_diacritics(self):
        forms = utils.get_all_related_forms("αβραν", True) #a(/bran
        
        self.assertEqual(len(forms), 6) 
