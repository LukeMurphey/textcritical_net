from django.conf.urls import patterns, include, url
from django.conf import settings
from grappelli import urls as grappelli_urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    # Include the Grappelli app                
    (r'^grappelli/', include(grappelli_urls)),
    
    # Include the reader app
    url(r'^', include('reader.urls')),

    # Enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # Serve static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
    
handler404 = 'reader.views.not_found_404'
handler500 = 'reader.views.not_found_404'