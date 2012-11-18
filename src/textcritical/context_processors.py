from django.conf import settings

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
    
    return settings_dict