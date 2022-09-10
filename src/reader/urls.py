from django.conf.urls import url, include
from reader.sitemaps import WorksSitemap, StaticSitemap
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps.views import sitemap
from reader import views

sitemaps = dict(
    static=StaticSitemap,
    works=WorksSitemap
)

urlpatterns = [
    # ----------------------------------
    # The following URLs are handled by the single-page app React app and just provide a
    # Javascript file which will do the REST calls.
    #
    # These don't need to be served by the Django backend since they just offer a static file.
    # BTW: some of these routes are called out specifically just so the backend can create URLs
    # for them. This is why I don't just route everything to the single_page_app view.
    # ----------------------------------
    url(r'^$', views.single_page_app, name='home'),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/(?P<leftovers>.+)/?$',
        views.single_page_app, name='read_work'),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/?$',
        views.single_page_app, name='read_work'),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/?$',
        views.single_page_app, name='read_work'),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/?$',
        views.single_page_app, name='read_work'),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/?$',
        views.single_page_app, name='read_work'),
    url(r'^work/(?P<title>.*)/(?P<division_0>.+)/?$',
        views.single_page_app, name='read_work'),
    url(r'^work/(?P<title>[^/]*)/?$', views.single_page_app, name='read_work'),

    url(r'^search/?$', views.single_page_app, name='search'),

    # These are largely just for historical reasons
    url(r'^about/?$', views.single_page_app, name='about'),
    url(r'^contact/?$', views.single_page_app, name='contact'),

    # This is the page that the user will be sent on once authentication is complete
    url(r'^auth_success/?$', views.single_page_app, name='auth_success'),

    # ----------------------------------
    # The following endpoints are those that are served by the backend and static file serving won't fulfill it
    # ----------------------------------
    url(r'^admin/reader/', include('reader.admin_urls')),

    url(r'^social_auth/?$', views.social_auth, name='social_auth'),
    url(r'^robots.txt/?$', views.robots_txt, name='robots_txt'),
    url(r'^humans.txt/?$', views.humans_txt, name='humans_txt'),
    url(r'^sitemap.xml$', sitemap, {'sitemaps': sitemaps}),

    # The following two links have been moved to be under /api but are kept here for historical reasons
    url(r'^download/work/(?P<title>.*)/?$',
        views.download_work, name='legacy_download_work'),
    url(r'^work_image/(?P<title>[^/]*)/?$',
        views.work_image, name='legacy_work_image'),

    # -----------------------------
    # API views
    # -----------------------------
    url(r'^api/?$', views.api_index, name='api_index'),

    url(r'^api/download/work/(?P<title>.*)/?$',
        views.download_work, name='download_work'),
    url(r'^api/work_image/(?P<title>[^/]*)/?$',
        views.work_image, name='work_image'),

    url(r'^api/betacode_to_unicode/(?P<text>[^/]*)/?$',
        views.api_beta_code_to_unicode, name='api_beta_code_to_unicode'),
    url(r'^api/unicode_to_betacode/(?P<text>[^/]*)/?$',
        views.api_unicode_to_betacode, name='api_unicode_to_betacode'),
    url(r'^api/version_info/?$', views.api_version_info, name='api_version_info'),
    url(r'^api/social_auth/?$', views.api_social_auth, name='api_social_auth'),
    
    url(r'^api/works_stats/?$', views.api_works_stats, name='api_works_stats'),
    url(r'^api/works/?$', views.api_works_list, name='api_works_list'),
    url(r'^api/word_parse_beta_code/(?P<word>[^/]*)/?$',
        views.api_word_parse_beta_code, name='api_word_parse_beta_code'),
    url(r'^api/word_parse/(?P<word>[^/]*)/?$',
        views.api_word_parse, name='api_word_parse'),
    url(r'^api/word_forms/(?P<word>.*)/?$',
        views.api_word_forms, name='api_word_forms'),
    url(r'^api/author_works/(?P<author>[^/]*)/?$',
        views.api_works_list_for_author, name='api_works_list_for_author'),
    url(r'^api/search_stats/(?P<search_text>.*)/?$',
        views.api_search_stats, name='api_search_stats'),
    url(r'^api/search/(?P<search_text>.*)/?$',
        views.api_search, name='api_search'),
    url(r'^api/convert_query_beta_code/(?P<search_query>[^/]*)/?$',
        views.api_convert_query_beta_code, name='api_convert_query_beta_code'),
    # url(r'^api/beta_code_to_unicode/(?P<beta_code>[^/]*)/?$', views.api_beta_code_to_unicode', name='api_beta_code_to_unicode' ),
    url(r'^api/beta_code_to_unicode/?$', views.api_beta_code_to_unicode,
        name='api_beta_code_to_unicode'),
    url(r'^api/resolve_reference/?$', views.api_resolve_reference,
        name='api_resolve_reference'),

    # Type-ahead hints for the list of works
    url(r'^api/works_typeahead_hints/?$', views.api_works_typeahead_hints,
        name='api_works_typeahead_hints'),

    # Reading works
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/(?P<leftovers>.+)/?$',
        views.api_read_work, name='api_read_work'),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/(?P<division_4>.+)/?$',
        views.api_read_work, name='api_read_work'),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/(?P<division_3>.+)/?$',
        views.api_read_work, name='api_read_work'),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/(?P<division_2>.+)/?$',
        views.api_read_work, name='api_read_work'),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/(?P<division_1>.+)/?$',
        views.api_read_work, name='api_read_work'),
    url(r'^api/work/(?P<title>.*)/(?P<division_0>.+)/?$',
        views.api_read_work, name='api_read_work'),
    url(r'^api/work/(?P<title>[^/]*)/?$',
        views.api_read_work, name='api_read_work'),

    # Wikipedia info
    url(r'^api/wikipedia_info/(?P<topic>[^/]*)/?$',
        views.api_wikipedia_info, name='api_wikipedia_info'),
    url(r'^api/wikipedia_info/(?P<topic>[^/]*)/(?P<topic2>[^/]*)/?$',
        views.api_wikipedia_info, name='api_wikipedia_info_2'),
    url(r'^api/wikipedia_info/(?P<topic>[^/]*)/(?P<topic2>[^/]*)/(?P<topic3>[^/]*)/?$',
        views.api_wikipedia_info, name='api_wikipedia_info_3'),

    # Information on works
    url(r'^api/work_info/(?P<title>[^/]*)/?$',
        views.api_work_info, name='api_work_info'),
    
    # User preferences
    url(r'^api/user_preferences/?$',
        views.api_user_preferences, name='api_user_preferences'),
    url(r'^api/user_preference/edit/(?P<name>[^/]*)/?$',
        views.api_user_preference_edit, name='api_user_preference_edit'),
    url(r'^api/user_preference/delete/(?P<name>[^/]*)/?$',
        views.api_user_preference_delete, name='api_user_preference_delete'),

    # Notes
    url(r'^api/notes/?$',
        views.api_notes, name='api_notes'),
    url(r'^api/note/(?P<note_id>[^/]*)/?$',
        views.api_note, name='api_note'),
    url(r'^api/note/(?P<note_id>[^/]*)/edit/?$',
        views.api_note_edit, name='api_note_edit'),
    url(r'^api/note/(?P<note_id>[^/]*)/delete/?$',
        views.api_note_delete, name='api_note_delete'),

]
