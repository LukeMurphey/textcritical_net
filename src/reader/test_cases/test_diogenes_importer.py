from . import TestReader, time_function_call
from reader.models import WordForm, Lemma
from reader.language_tools.greek import Greek
from reader.importer.Diogenes import DiogenesLemmataImporter

class TestDiogenesLemmaImport(TestReader):    
    
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
    
    @time_function_call
    def test_import_file(self):
        
        lemmas = DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        self.assertEquals(len(lemmas), 95)
    
    def test_parse(self):
        
        f = open(self.get_test_resource_file_name("greek-lemmata.txt"), 'r')
        s = f.readline()
        
        lemma = DiogenesLemmataImporter.parse_lemma(s)
        
        self.assertEquals(lemma.lexical_form, Greek.beta_code_str_to_unicode("a(/bra"))
        self.assertEquals(lemma.reference_number, 537850)
