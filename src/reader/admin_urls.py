from django.urls import re_path
from reader.admin_views import import_perseus_file

urlpatterns = [
                re_path(r'^work/import_perseus_file/?$', import_perseus_file, name="admin_import_perseus_file"),
              ] 