from . import TestReader, time_function_call
from reader.importer.Diogenes import DiogenesLemmataImporter, DiogenesAnalysesImporter
from reader.models import WordDescription, Lemma, WordForm
from reader.language_tools.greek import Greek

class TestDiogenesAnalysesImport(TestReader):
    
    @time_function_call
    def test_import_file(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
        # See if the analyses match up with the lemmas
        # Find the word description and make sure the lemma matches
        descriptions = WordDescription.objects.filter(meaning="favourite slave")
        
        self.assertEqual(descriptions[0].lemma.reference_number, 537850)
        self.assertEqual(descriptions[0].meaning, "favourite slave")
        
    def test_import_file_no_match(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata-no-match.txt"), return_created_objects=True)
        
        # Import the analyses
        analyses = DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses-no-match.txt"), return_created_objects=True, raise_exception_on_match_failure=True)
        
        self.assertEqual(len(analyses), 4)
        
    @time_function_call
    def test_lookup_by_form(self):
        
        # Get the lemmas so that we can match up the 
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
        # See if the analyses match up with the lemmas
        # Find the word description and make sure the lemma matches
        
        descriptions = WordDescription.objects.filter(word_form__form=Greek.beta_code_str_to_unicode("a(/bra"))
        
        self.assertEqual(descriptions[0].lemma.reference_number, 537850)
        self.assertEqual(descriptions[0].meaning, "favourite slave")
        
        
    def make_lemma(self):
        lemma = Lemma(lexical_form=Greek.beta_code_str_to_unicode("a(/bra"), language="Greek", reference_number=537850)
        lemma.save()
        
        return lemma
    
    def make_form(self):
        
        lemma = self.make_lemma()
        
        word_form = WordForm()
        word_form.lemma = lemma
        word_form.form = Greek.beta_code_str_to_unicode("a(/bra")
        word_form.save()
        
        return word_form
        
    def test_handle_multiple_genders(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        word_form = self.make_form()
        
        description = DiogenesAnalysesImporter.import_analysis_entry("537850 9 a_)ghko/ti,a)ga/w\t \tperf part act masc/neut dat sg (attic doric ionic aeolic)}" , word_form)
        
        self.assertTrue(description.masculine)
        self.assertTrue(description.neuter)
        self.assertFalse(description.feminine)
        
    def test_handle_no_match(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata-no-match.txt"), return_created_objects=True)
        
        word_form = self.make_form()
        
        #full_entry = "e)pamfie/sasqai\t{31475848 9 e)pamfi+e/sasqai,e)pi/,a)mfi/-e(/zomai\tseat oneself\taor inf mid (attic epic doric ionic aeolic parad_form prose)}[40532015][6238652]{6264700 9 e)pi/-a)mfia/zw\tciothe\taor inf mid}[40532015]{6365952 9 e)pi/-a)mfie/nnumi\tput round\taor inf mid (attic)}[40532015]"
        
        word_description = DiogenesAnalysesImporter.import_analysis_entry("e)pamfie/sasqai\t{31475848 9 e)pamfi+e/sasqai,e)pi/,a)mfi/-e(/zomai\tseat oneself\taor inf mid (attic epic doric ionic aeolic parad_form prose)}[40532015][6238652]", word_form)
        
        self.assertNotEqual(word_description, None)
        
    def test_parse_no_match(self):
        
        word_form = WordForm()
        word_form.form = "test_parse_no_match"
        word_form.save()
        
        desc = "Wont match regex"
        
        # Make sure this does not trigger an exception
        self.assertEqual(DiogenesAnalysesImporter.import_analysis_entry(desc, word_form), None)
    