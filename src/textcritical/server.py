from django.core.wsgi import get_wsgi_application
import wsgiserver

def start_server( address="0.0.0.0", port=8080):
    
    """
    server = wsgiserver.WSGIServer(
        (address, port),  # Use '127.0.0.1' to only bind to the localhost
        get_wsgi_application()
    )
    """

    server = wsgiserver.WSGIServer(get_wsgi_application(), host=address, port=port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print('Stopping server')
        server.stop()
