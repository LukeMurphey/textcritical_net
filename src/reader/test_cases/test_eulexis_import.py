from . import TestReader, time_function_call
from reader.importer.Eulexis import EulexisAnalysesImporter
from reader.models import WordDescription, Lemma, WordForm
from reader.language_tools.greek import Greek


class TestEulexisAnalysesImport(TestReader):

    @time_function_call
    def test_import_file(self):
        lemmas = EulexisAnalysesImporter.import_file(self.get_test_resource_file_name(
            "greek-lemmata.txt"), return_created_objects=True)

        self.assertEquals(len(lemmas), 95)
