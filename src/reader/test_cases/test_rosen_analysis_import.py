from . import TestReader, time_function_call
from reader.importer.Rosen import RosenAnalysesImporter
from reader.models import WordDescription, Lemma, WordForm
from reader.language_tools.greek import Greek

class TestRosenAnalysesImport(TestReader):
    
    @time_function_call
    def test_import_file(self):
        
        # Get the analyses
        words = RosenAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses-unicode-babylon-with-variants-BOM.txt"), return_created_objects=True, raise_exception_on_match_failure=True)
        
        self.assertEqual(len(words), 16)

        self.assertEqual(words[0].word_form.form, "άβαις")
        self.assertEqual(words[0].word_form.basic_form, "αβαις")

        self.assertEqual(words[0].lemma.lexical_form, "ἥβη")
        self.assertEqual(words[0].lemma.language, "Greek")
        self.assertEqual(words[0].meaning, "youthful prime")

        # Check the word description
        # Gender
        self.assertEqual(words[0].feminine, True)
        self.assertEqual(words[0].masculine, False)
        self.assertEqual(words[0].neuter, False)

        # Case
        first_case = words[0].cases.get()
        self.assertEqual(first_case.name, "dative")

        # Number
        self.assertEqual(words[0].number, WordDescription.PLURAL)

        # Dialects
        first_dialect = words[0].dialects.get()
        self.assertEqual(first_dialect.name, "doric")

    @time_function_call
    def test_import_file_lemma_dupes(self):

        # Count the number of lemmas
        numberAtBeginning = Lemma.objects.count()
        
        # Get the analyses
        words = RosenAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses-unicode-babylon-with-variants-BOM-dupes.txt"), return_created_objects=True, raise_exception_on_match_failure=True)
        
        self.assertEqual(len(words), 126)

        # Count the number of lemmas
        numberAtEnd = Lemma.objects.count()

        self.assertEqual(numberAtEnd - numberAtBeginning, 2)

    @time_function_call
    def test_import_file_form_dupes(self):

        # Count the number of lemmas
        numberAtBeginning = WordForm.objects.count()
        
        # Get the analyses
        words = RosenAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses-unicode-babylon-with-variants-BOM-dupes.txt"), return_created_objects=True, raise_exception_on_match_failure=True)

        # Count the number of word forms
        numberAtEnd = WordForm.objects.count()

        self.assertEqual(numberAtEnd - numberAtBeginning, 40)

        # Do it again; verify that zero new objects are created
        numberAtBeginning = WordForm.objects.count()
        RosenAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses-unicode-babylon-with-variants-BOM-dupes.txt"), return_created_objects=True, raise_exception_on_match_failure=True)
        numberAtEnd = WordForm.objects.count()
        self.assertEqual(numberAtEnd - numberAtBeginning, 0)
