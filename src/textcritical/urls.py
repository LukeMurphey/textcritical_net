from django.urls import include, re_path
from django.urls import path
from django.conf import settings
from django.views.static import serve
from grappelli import urls as grappelli_urls
import reader.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler404 = reader.views.not_found_404
handler500 = reader.views.error_500

urlpatterns = [
    
    # Include the Grappelli app
    re_path(r'^grappelli/', include(grappelli_urls)),
    
    # Include the reader app
    re_path(r'^', include('reader.urls')),

    # Enable admin documentation:
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Enable the admin:
    re_path(r'^admin/', admin.site.urls),

    # For social logins
    path('accounts/', include('allauth.urls')),

    # Serve static files (images, css, javascript, etc.):
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT
    }),
]
