import os, sys

def get_setting_or_default( setting, default=None ):
    try:
        return getattr(settings, setting)
    except AttributeError:
        return default

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    
    # Set the path to the application directory
    sys.path.append( os.path.join( os.getcwd(), "textcritical" ) )
    
    from django.conf import settings
    
    # Import the function necessary to start the server
    from textcritical.server import start_server
    
    # Get the server and port from the settings
    address = get_setting_or_default( "WEB_SERVER_ADDRESS", default="0.0.0.0" )
    port = get_setting_or_default( "WEB_SERVER_PORT", default="8080" )
    
    start_server( address, port )