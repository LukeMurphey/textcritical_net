from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^/?$', 'reader.views.home', name='home' ),
    url(r'^books/?$', 'reader.views.books_index', name='book_index' )
)