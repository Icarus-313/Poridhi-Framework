def poridhi_app(environ, start_response):

    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    
    # Return the greeting message
    return [b'Hello, Welcome to Poridhi!']

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    # Create a WSGI server
    server = make_server('', 8000, poridhi_app)
    
    print("Serving on port 8000...")
    
    # Serve until process is killed
    server.serve_forever()