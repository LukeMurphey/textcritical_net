from django.test import TestCase
from reader.models import UserPreference
from django.contrib.auth.models import User

class TestUserPreference(TestCase):
        
    def test_create_dup_user_preference(self):
        user = User.objects.create_user(username='testuser', password='12345')

        value_string = '[{"workTitleSlug":"new-testament","divisions":["John"],"divisionReference":"John 1"},{"workTitleSlug":"berean-study-bible","divisions":["Galatians","6"],"divisionReference":"Galatians 6"},{"workTitleSlug":"antiquitates-judaicae","divisions":[],"divisionReference":"1 pr."},{"workTitleSlug":"antiquities-of-the-jews","divisions":[],"divisionReference":"1 pr."},{"workTitleSlug":"ajax","divisions":[],"divisionReference":"1"}]'
        setting = UserPreference(user=user, name="favorite_books", value=value_string)
        setting.save()

        setting2 = UserPreference(user=user, name="favorite_books", value=value_string)
        setting2.save()
