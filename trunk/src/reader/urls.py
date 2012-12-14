from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^admin/reader/', include('reader.admin_urls')),
    
    url(r'^robots.txt/?$', 'reader.views.robots_txt', name='robots_txt' ),
    url(r'^humans.txt/?$', 'reader.views.humans_txt', name='humans_txt' ),
    
    url(r'^/?$', 'reader.views.home', name='home' ),
    url(r'^works/?$', 'reader.views.works_index', name='works_index' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>[^/]*)/?$', 'reader.views.read_work', name='read_work' ),
    
    url(r'^about/?$', 'reader.views.about', name='about' ),
    url(r'^contact/?$', 'reader.views.contact', name='contact' ),
    
    # API views
    url(r'^api/?$', 'reader.views.api_index', name='api_index' ),
    url(r'^api/betacode-to-unicode/?$', 'reader.views.api_beta_code_to_unicode', name='api_beta_code_to_unicode' ),
    url(r'^api/works/?$', 'reader.views.api_works_list', name='api_works_list' )
)