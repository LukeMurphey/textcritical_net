from django.conf.urls import url, include
from reader.sitemaps import WorksSitemap, StaticSitemap
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps.views import sitemap
from reader import views

sitemaps = dict(
                static = StaticSitemap,
                works = WorksSitemap
                )

urlpatterns = [
    url(r'^admin/reader/', include('reader.admin_urls')),

    url(r'^robots.txt/?$', views.robots_txt, name='robots_txt' ),
    url(r'^humans.txt/?$', views.humans_txt, name='humans_txt' ),
    url(r'^sitemap.xml$', sitemap, {'sitemaps': sitemaps}),

    url(r'^$', views.works_index, name='home' ),
    
    url(r'^download/work/(?P<title>.*)/?$', views.download_work, name='download_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/(?P<leftovers>.+)/?$', views.read_work, name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/?$', views.read_work, name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/?$', views.read_work, name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/?$', views.read_work, name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/?$', views.read_work, name='read_work' ),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/?$', views.read_work, name='read_work' ),
    url(r'^work/(?P<title>[^/]*)/?$', views.read_work, name='read_work' ),
    
    url(r'^work_image/(?P<title>[^/]*)/?$', views.work_image, name='work_image' ),

    url(r'^about/?$', views.about, name='about' ),
    url(r'^contact/?$', views.contact, name='contact' ),
    url(r'^search/?$', views.search, name='search' ),
    
    url(r'^word_forms/?$', views.word_forms, name='word_forms' ),
    url(r'^beta_code_converter/?$', views.beta_code_converter, name='beta_code_converter' ),
    
    url(r'^tests/?$', views.tests, name='tests' ),

    # This is now the home page. This is kept around for historical reasons.
    url(r'^works/?$', views.works_index, name='works_index' ),
    
    # API views
    url(r'^api/?$', views.api_index, name='api_index' ),
    url(r'^api/betacode_to_unicode/(?P<text>[^/]*)/?$', views.api_beta_code_to_unicode, name='api_beta_code_to_unicode' ),
    url(r'^api/unicode_to_betacode/(?P<text>[^/]*)/?$', views.api_unicode_to_betacode, name='api_unicode_to_betacode' ),
    
    url(r'^api/works/?$', views.api_works_list, name='api_works_list' ),
    url(r'^api/word_parse_beta_code/(?P<word>[^/]*)/?$', views.api_word_parse_beta_code, name='api_word_parse_beta_code' ),
    url(r'^api/word_parse/(?P<word>[^/]*)/?$', views.api_word_parse, name='api_word_parse' ),
    url(r'^api/word_forms/(?P<word>.*)/?$', views.api_word_forms, name='api_word_forms' ),
    url(r'^api/author_works/(?P<author>[^/]*)/?$', views.api_works_list_for_author, name='api_works_list_for_author' ),
    url(r'^api/search_stats/(?P<search_text>.*)/?$', views.api_search_stats, name='api_search_stats' ),
    url(r'^api/search/(?P<search_text>.*)/?$', views.api_search, name='api_search' ),
    url(r'^api/convert_query_beta_code/(?P<search_query>[^/]*)/?$', views.api_convert_query_beta_code, name='api_convert_query_beta_code' ),
    #url(r'^api/beta_code_to_unicode/(?P<beta_code>[^/]*)/?$', views.api_beta_code_to_unicode', name='api_beta_code_to_unicode' ),
    url(r'^api/beta_code_to_unicode/?$', views.api_beta_code_to_unicode, name='api_beta_code_to_unicode' ),
    url(r'^api/resolve_reference/?$', views.api_resolve_reference, name='api_resolve_reference' ),
    
    url(r'^api/works_typeahead_hints/?$', views.api_works_typeahead_hints, name='api_works_typeahead_hints' ),

    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/(?P<leftovers>.+)/?$', views.api_read_work, name='api_read_work' ),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/?$', views.api_read_work, name='api_read_work' ),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/?$', views.api_read_work, name='api_read_work' ),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/?$', views.api_read_work, name='api_read_work' ),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/?$', views.api_read_work, name='api_read_work' ),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/?$', views.api_read_work, name='api_read_work' ),
    url(r'^api/work/(?P<title>[^/]*)/?$', views.api_read_work, name='api_read_work' ),
    
    url(r'^api/wikipedia_info/(?P<topic>[^/]*)/?$', views.api_wikipedia_info, name='api_wikipedia_info' ),
    url(r'^api/wikipedia_info/(?P<topic>[^/]*)/(?P<topic2>[^/]*)/?$', views.api_wikipedia_info, name='api_wikipedia_info_2' ),
    url(r'^api/wikipedia_info/(?P<topic>[^/]*)/(?P<topic2>[^/]*)/(?P<topic3>[^/]*)/?$', views.api_wikipedia_info, name='api_wikipedia_info_3' ),

    url(r'^api/work_info/(?P<title>[^/]*)/?$', views.api_work_info, name='api_work_info' ),
    
]