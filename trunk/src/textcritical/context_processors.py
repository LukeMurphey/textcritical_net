from django.conf import settings
from django.core.urlresolvers import resolve

def get_setting_or_default( setting, default=None ):
    try:
        return getattr(settings, setting)
    except AttributeError:
        return default

def add_to_dict( d, name, value ):
    d[name] = value


def is_request_async(request):

    if 'async' in request.GET and request.GET['async'] == "0":
        return False
    elif 'async' in request.GET:
        return True
    
    return request.is_ajax()

def is_async(request):
        
    return {
           'is_async': is_request_async(request)
    }

def global_settings(request):
    
    settings_dict = {}
    
    settings_dict['USE_DARK_THEME'] = get_setting_or_default("USE_DARK_THEME", False)
    settings_dict['USE_MINIFIED'] = get_setting_or_default("USE_MINIFIED", False)
    
    return settings_dict

def get_url_name(request):
    return {
       'url_name': resolve(request.path_info).url_name
     }