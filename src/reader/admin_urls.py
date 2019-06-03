from django.conf.urls import *
from reader.admin_views import import_perseus_file

urlpatterns = [
                url(r'^work/import_perseus_file/?$', import_perseus_file, name="admin_import_perseus_file"),
              ] 