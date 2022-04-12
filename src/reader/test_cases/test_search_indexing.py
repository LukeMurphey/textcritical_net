import os
import shutil

from . import TestReader
from reader.models import Author, Work, Division, Verse
from reader.contentsearch import WorkIndexer, search_verses, search_stats

class TestWorkIndexer(WorkIndexer):
    
    @classmethod
    def get_index_dir(cls):
        return os.path.join("..", "var", "tests", "indexes")
    
    @classmethod
    def delete_index(cls):
        shutil.rmtree(cls.get_index_dir(), ignore_errors=True)
    
class TestContentSearch(TestReader):
    
    indexer = None
    
    def setUp(self):
        
        self.indexer = TestWorkIndexer
        
        # Remove any existing index files from previous tests
        self.indexer.delete_index()

    def make_work(self, content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.", division_title="test_add_doc(division)", work_title="test_add_doc", work_title_slug=None, division_title_slug=None, division_descriptor=None):
        author = Author()
        author.name = "Luke"
        author.save()
        
        work = Work(title=work_title)
        
        if work_title_slug:
            work.title_slug = work_title_slug
        
        work.save()
        
        division = Division(work=work, title=division_title, readable_unit=True, level=1, sequence_number=1)
        
        if division_title_slug:
            division.title_slug = division_title_slug
            
        if division_descriptor:
            division.descriptor = division_descriptor
        
        division.save()
        
        verse = Verse(division=division, indicator="1", sequence_number=1, content=content)
        verse.save()
        
        return verse, division, work
    
    def tearDown(self):
        
        # Remove the index files so they don't cause problems with future tests
        self.indexer.delete_index()
    
    def test_index_verse(self):
        
        # Make a work
        verse, division, work = self.make_work()
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses("amet", self.indexer.get_index())
        
        self.assertEqual(len(results.verses), 1)
        self.assertEqual(results.matched_terms.get('amet', -1), 1)
        self.assertEqual(results.matched_terms_no_diacritics.get('amet', -1), 1)
        
    def test_search_verse_no_diacritic(self):
        
        # Make a work
        verse, division, work = self.make_work("ἐξ ἔργων νόμου οὐ δικαιωθήσεται πᾶσα σὰρξ")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses("no_diacritics:νομου", self.indexer.get_index())
        
        self.assertEqual(len(results.verses), 1)
        
    def test_search_verse_beta_code(self):
        
        # Make a work
        verse, division, work = self.make_work("ἐξ ἔργων νόμου οὐ δικαιωθήσεται πᾶσα σὰρξ")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses('NO/MOU', self.indexer.get_index())
        
        self.assertEqual(len(results.verses), 1)
        
    def test_search_verse_beta_code_no_diacritics(self):
        
        # Make a work
        verse, division, work = self.make_work("ἐξ ἔργων νομου οὐ δικαιωθήσεται πᾶσα σὰρξ")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses("NOMOU", self.indexer.get_index())
        
        self.assertEqual(len(results.verses), 1)
    
    def test_search_verse_work_by_slug(self):
        
        # Make a work
        verse, division, work = self.make_work(work_title="New Testament", work_title_slug="test_search_verse_work_by_slug")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses("work_id:test_search_verse_work_by_slug", self.indexer.get_index())
        self.assertEqual(len(results.verses), 1)
        
        results = search_verses("work:test_search_verse_work_by_slug", self.indexer.get_index())
        self.assertEqual(len(results.verses), 1)

        results = search_verses('work:"New Testament"', self.indexer.get_index())
        self.assertEqual(len(results.verses), 1)
        
    def test_search_division_by_slug(self):
        
        # Make a work
        verse, division, work = self.make_work(division_title="Some Division", division_descriptor="division_descriptor")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses("section:division_descriptor", self.indexer.get_index())
        self.assertEqual(len(results.verses), 1)

        results = search_verses('section:"Some Division"', self.indexer.get_index())
        self.assertEqual(len(results.verses), 1)
        
    def test_index_work(self):
        
        # Make a work
        verse, division, work = self.make_work()
        
        self.indexer.get_index(create=True)
        self.indexer.index_work(work)
        
        results = search_verses("amet", self.indexer.get_index())
        
        self.assertEqual(len(results.verses), 1)
        
    def test_index_division(self):
        
        # Make a work
        verse, division, work = self.make_work()
        
        self.indexer.get_index(create=True)
        self.indexer.index_division(division)
        
        results = search_verses("amet", self.indexer.get_index())
        
        self.assertEqual(len(results.verses), 1)
        
    def test_matched_terms(self):
        
        # Make a work
        verse, division, work = self.make_work("οὐ νοεῖτε ὅτι πᾶν τὸ εἰσπορευόμενον εις τὸ στόμα εἰς τὴν κοιλίαν χωρεῖ καὶ εἰς ἀφεδρῶνα ἐκβάλλεται;")
        
        self.indexer.get_index(create=True)
        self.indexer.index_division(division)
        
        results = search_verses("no_diacritics:εις τὸ", self.indexer.get_index())
        
        self.assertEqual(len(results.verses), 1)
        self.assertEqual(len(results.matched_terms), 1)
        self.assertEqual(results.matched_terms.get('τὸ', -1), 1)
        self.assertEqual(results.matched_terms_no_diacritics.get('τὸ', -1), 1)
        
    def test_search_stats(self):
        
        # Make a work
        verse, division, work = self.make_work("οὐ νοεῖτε ὅτι πᾶν τὸ εἰσπορευόμενον εἰς τὸ στόμα εἰς τὴν κοιλίαν χωρεῖ καὶ εἰς ἀφεδρῶνα ἐκβάλλεται;")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_stats("εἰς OR τὸ", self.indexer.get_index())
        
        self.assertEqual(results['matches'], 5)
        self.assertEqual(results['matched_terms']["εἰς"], 3)
        self.assertEqual(results['matched_terms']["τὸ"], 2)
        
    def test_search_stats_no_diacritics(self):
        
        # Make a work
        verse, division, work = self.make_work("οὐ νοεῖτε ὅτι πᾶν τὸ εἰσπορευόμενον εἰς τὸ στόμα εἰς τὴν κοιλίαν χωρεῖ καὶ εἰς ἀφεδρῶνα ἐκβάλλεται;")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_stats("εἰς OR no_diacritics:το", self.indexer.get_index())
        
        self.assertEqual(results['matches'], 5)
        self.assertEqual(results['matched_terms']["εἰς"], 3)
        self.assertEqual(results['matched_terms']["το"], 2)
