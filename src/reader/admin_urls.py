from django.conf.urls import *

urlpatterns = patterns('',
                       url(r'^work/import_perseus_file/?$', 'reader.admin_views.import_perseus_file', name="admin_import_perseus_file"),
                       )