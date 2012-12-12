import django.core.handlers.wsgi

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