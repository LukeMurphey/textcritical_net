import django.core.handlers.wsgi
from django.conf import settings

import os, sys

def get_setting_or_default( setting, default=None ):
    try:
        return getattr(settings, setting)
    except AttributeError:
        return default

def start_server( address="0.0.0.0", port=8080):
    from textcritical import wsgiserver
    
    server = wsgiserver.CherryPyWSGIServer(
        (address, port),  # Use '127.0.0.1' to only bind to the localhost
        django.core.handlers.wsgi.WSGIHandler()
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        print 'Stopping server'
        server.stop()

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    
    sys.path.append(os.path.realpath( os.path.dirname( os.path.dirname(__file__) ) ) )
    
    # Get the server and port from the settings
    address = get_setting_or_default( "WEB_SERVER_ADDRESS", default="0.0.0.0" )
    port = get_setting_or_default( "WEB_SERVER_PORT", default="8080" )
    
    start_server( address, port )
