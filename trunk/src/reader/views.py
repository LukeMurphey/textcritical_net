# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext

def home(request):
    return render_to_response('index.html',
                              {},
                              context_instance=RequestContext(request))

def books_index(request):
    return render_to_response('index.html',
                              { 'books' : []},
                              context_instance=RequestContext(request))
