from . import TestReader
from reader.models import Work, WorkAlias

class TestWorkAlias(TestReader):
    
    def test_make_alias(self):
        work = Work(title="Test make alias", title_slug="test-make-alias")
        work.save()
        
        # Modify the slug so that the automatically created alias (happens when a work is saved) won't match
        work.title_slug = work.title_slug + "-makes-it-unique"
        
        work_alias = WorkAlias.populate_alias_from_work(work)
        
        self.assertNotEqual(work_alias, None)
        self.assertEqual(WorkAlias.objects.filter(work=work, title_slug=work.title_slug).count(), 1)
        
    def test_make_alias_automatic(self):
        work = Work(title="Test make alias", title_slug="test-make-alias")
        work.save()
        
        work_alias = WorkAlias.populate_alias_from_work(work)
        
        # Make sure that the alias was made automatically
        self.assertEqual(work_alias, None)
        self.assertEqual(WorkAlias.objects.filter(work=work, title_slug=work.title_slug).count(), 1)
    
    def test_make_alias_detect_overlap(self):
        
        work = Work(title="Test make alias", title_slug="test_make_alias_detect_overlap")
        work.save()
        
        # Make sure the alias exists
        work_alias = WorkAlias.populate_alias_from_work(work)
        self.assertEqual(work_alias, None)
        
        work.title_slug = "test-make-alias-new"
        work.save()
        
        work2 = Work(title="Test make alias", title_slug="test_make_alias_detect_overlap")
        
        def populate():
            WorkAlias.populate_alias_from_work(work2)
        
        self.assertRaises(Exception, populate)
    
    def test_make_alias_already_exists(self):
        
        work = Work(title="Test_make_alias_ignore_overlap", title_slug="test_make_alias_ignore_overlap")
        work.save()
        
        # Modify the slug so that the automatically created alias (happens when a work is saved) won't match
        work.title_slug = work.title_slug + "-makes-it-unique"
        
        self.assertNotEqual(WorkAlias.populate_alias_from_work(work), None)
        self.assertEqual(WorkAlias.populate_alias_from_work(work), None)
    
    def test_populate_aliases(self):
        work = Work(title="Test_make_alias_ignore_overlap", title_slug="test_make_alias_ignore_overlap")
        work.save()
        
        work2 = Work(title="Test_make_alias_ignore_overlap", title_slug="test_make_alias_ignore_overlap2")
        work2.save()
        
        # Remove the automatically created aliases
        WorkAlias.objects.filter(title_slug="test_make_alias_ignore_overlap").delete()
        WorkAlias.objects.filter(title_slug="test_make_alias_ignore_overlap2").delete()
        
        # Now see if populate_from_existing re-creates them
        self.assertEqual(WorkAlias.populate_from_existing(), 2)
