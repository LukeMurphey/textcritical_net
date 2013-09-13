from django.conf.urls import patterns, url, include
from reader.sitemaps import WorksSitemap, StaticSitemap

sitemaps = dict(
                static = StaticSitemap,
                works = WorksSitemap
                )

urlpatterns = patterns('',
    url(r'^admin/reader/', include('reader.admin_urls')),
    
    url(r'^robots.txt/?$', 'reader.views.robots_txt', name='robots_txt' ),
    url(r'^humans.txt/?$', 'reader.views.humans_txt', name='humans_txt' ),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
    url(r'^/?$', 'reader.views.home', name='home' ),
    url(r'^works/?$', 'reader.views.works_index', name='works_index' ),
    url(r'^download/work/(?P<title>.*)/?$', 'reader.views.download_work_epub', name='download_work_epub' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/(?P<leftovers>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/?$', 'reader.views.read_work', name='read_work' ),
    url(r'^work/(?P<title>[^/]*)/?$', 'reader.views.read_work', name='read_work' ),
    
    url(r'^about/?$', 'reader.views.about', name='about' ),
    url(r'^contact/?$', 'reader.views.contact', name='contact' ),
    url(r'^search/?$', 'reader.views.search', name='search' ),
    url(r'^beta_code_converter/?$', 'reader.views.beta_code_converter', name='beta_code_converter' ),
    
    url(r'^tests/?$', 'reader.views.tests', name='tests' ),
    
    # API views
    url(r'^api/?$', 'reader.views.api_index', name='api_index' ),
    url(r'^api/betacode_to_unicode/(?P<text>[^/]*)/?$', 'reader.views.api_beta_code_to_unicode', name='api_beta_code_to_unicode' ),
    url(r'^api/unicode_to_betacode/(?P<text>[^/]*)/?$', 'reader.views.api_unicode_to_betacode', name='api_unicode_to_betacode' ),
    
    url(r'^api/works/?$', 'reader.views.api_works_list', name='api_works_list' ),
    url(r'^api/word_parse_beta_code/(?P<word>[^/]*)/?$', 'reader.views.api_word_parse_beta_code', name='api_word_parse_beta_code' ),
    url(r'^api/word_parse/(?P<word>[^/]*)/?$', 'reader.views.api_word_parse', name='api_word_parse' ),
    url(r'^api/author_works/(?P<author>[^/]*)/?$', 'reader.views.api_works_list_for_author', name='api_works_list_for_author' ),
    url(r'^api/search/(?P<search_text>[^/]*)/?$', 'reader.views.api_search', name='api_search' ),
    url(r'^api/convert_query_beta_code/(?P<search_query>[^/]*)/?$', 'reader.views.api_convert_query_beta_code', name='api_convert_query_beta_code' ),
    #url(r'^api/beta_code_to_unicode/(?P<beta_code>[^/]*)/?$', 'reader.views.api_beta_code_to_unicode', name='api_beta_code_to_unicode' ),
    url(r'^api/beta_code_to_unicode/?$', 'reader.views.api_beta_code_to_unicode', name='api_beta_code_to_unicode' ),
    url(r'^api/resolve_reference/?$', 'reader.views.api_resolve_reference', name='api_resolve_reference' ),
    
    url(r'^api/works_typehead_hints/?$', 'reader.views.api_works_typehead_hints', name='api_works_typehead_hints' ),
    
    
    
)