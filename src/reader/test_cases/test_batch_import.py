from django.test import TestCase
from reader.models import Work, Author, Division
from reader.importer.batch_import import ImportTransforms


class TestBatchImport(TestCase):
    
    def test_update_title_slug(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        ImportTransforms.update_title_slug(work, "english")
        
        self.assertEqual(work.title_slug, "some-doc-english")
        
    def test_update_title_slug_default(self):
        
        work = Work(title="Some Doc", language="Greek")
        work.save()
        
        ImportTransforms.update_title_slug(work)
        
        self.assertEqual(work.title_slug, "some-doc-greek")
     
    def test_update_title_slug_by_editor(self):
        
        editor = Author(name="William Whiston")
        editor.save()
        
        work = Work(title="Some Doc", language="English")
        work.save()
        
        work.editors.add(editor)
        
        ImportTransforms.update_title_slug(work)
        
        self.assertEqual(work.title_slug, "some-doc-whiston")

     
    def test_update_title_slug_by_editor_with_extra(self):
        
        editor = Author(name="William Whiston, Ph. D.")
        editor.save()
        
        work = Work(title="Some Doc", language="English")
        work.save()
        
        work.editors.add(editor)
        
        ImportTransforms.update_title_slug(work)
        
        self.assertEqual(work.title_slug, "some-doc-whiston")   
        
    def test_set_division_title(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        for i in range(1,20):
            division = Division(title="Test" + str(i), sequence_number=i, work=work, level=1)
            division.save()
        
        ImportTransforms.set_division_title(work, existing_division_sequence_number=18, descriptor="NewDesc")
        
        self.assertEqual(Division.objects.get(work=work, sequence_number=18).descriptor, "NewDesc")
        
    def test_set_division_title_by_parent(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        for i in range(1,20):
            
            parent_division = Division(title="parent" + str(i), original_title="parent" + str(i), sequence_number=i, work=work, level=1)
            parent_division.save()
            
            division = Division(title="child" + str(i), original_title="child" + str(i), sequence_number=i+100, work=work, level=2, parent_division=parent_division)
            division.save()
        
        ImportTransforms.set_division_title(work, existing_division_parent_title_slug="parent18", existing_division_title_slug="child18", descriptor="NewDesc")
        
        self.assertEqual(Division.objects.get(work=work, sequence_number=118).descriptor, "NewDesc")
        
    """
    def test_set_verse_title(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        division = Division(title="test_set_verse_title", original_title="test_set_verse_title", sequence_number=1, work=work, level=1)
        division.save()
        
        for i in range(1,5):
            verse = Verse(title=str(i), sequence_number=i, division=division)
            verse.save()
        
        ImportTransforms.set_verse_title(work, existing_verse_sequence_number=3, existing_verse_title_slug="3", descriptor="Intro")
        
        self.assertEqual(Verse.objects.get(work=work, sequence_number=3).descriptor, "Intro")
    """
    
    def test_set_division_readable(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        for i in range(1,20):
            
            parent_division = Division(title=str(i), original_title=str(i), sequence_number=i, work=work, level=1, type="Book", descriptor=str(i), readable_unit=False)
            parent_division.save()
            
            division = Division(title=str(i), original_title=str(i), sequence_number=i+100, work=work, level=2, parent_division=parent_division, type="Chapter", descriptor="1", readable_unit=False)
            division.save()
        
        ImportTransforms.set_division_readable(work, sequence_number=110, title_slug="10", type="Chapter", descriptor="1", level=2)
        
        self.assertEqual(Division.objects.get(work=work, sequence_number=110).readable_unit, True)
