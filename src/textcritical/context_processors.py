from django.conf import settings
from django.core.urlresolvers import resolve

def get_setting_or_default( setting, default=None ):
    try:
        return getattr(settings, setting)
    except AttributeError:
        return default

def add_to_dict( d, name, value ):
    d[name] = value

def global_settings(request):
    
    settings_dict = {}
    
    settings_dict['USE_DARK_THEME'] = get_setting_or_default("USE_DARK_THEME", False)
    settings_dict['USE_MINIFIED'] = get_setting_or_default("USE_MINIFIED", False)
    
    return settings_dict

def get_url_name(request):
    return {
       'url_name': resolve(request.path_info).url_name
     }