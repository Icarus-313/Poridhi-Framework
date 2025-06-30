import json
from urllib.parse import parse_qs

class Request:
    """
    Represents an HTTP request with easy access to common data
    """
    def __init__(self, environ):
        self.environ = environ
        self.path = environ['PATH_INFO']
        self.method = environ['REQUEST_METHOD']
        
        # Parse query parameters (?name=value&age=25)
        query_string = environ.get('QUERY_STRING', '')
        self.params = parse_qs(query_string)
        
        # Flatten single-value parameters
        for key, value in self.params.items():
            if len(value) == 1:
                self.params[key] = value[0]

class Response:
    """
    Represents an HTTP response
    """
    def __init__(self):
        self.status = '200 OK'
        self.headers = [('Content-Type', 'text/html')]
        self.body = ''
    
    def json(self, data):
        """Return JSON response"""
        self.headers = [('Content-Type', 'application/json')]
        self.body = json.dumps(data)
        return self

class WebFramework:
    def __init__(self):
        self.routes = {}
    
    def route(self, path):
        def wrapper(handler_func):
            self.routes[path] = handler_func
            return handler_func
        return wrapper
    
    def __call__(self, environ, start_response):
        # Create request object
        request = Request(environ)
        
        # Check if route exists
        if request.path in self.routes:
            try:
                # Call handler with request object
                result = self.routes[request.path](request)
                
                # Handle different response types
                if isinstance(result, Response):
                    start_response(result.status, result.headers)
                    body = result.body
                else:
                    # Simple string response
                    start_response('200 OK', [('Content-Type', 'text/html')])
                    body = result
                
                # Ensure response is bytes
                if isinstance(body, str):
                    body = body.encode('utf-8')
                
                return [body]
                
            except Exception as e:
                # Handle errors gracefully
                start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
                return [f'<h1>Error:</h1><p>{str(e)}</p>'.encode('utf-8')]
        else:
            # 404 Not Found
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b'<h1>404 - Page Not Found</h1>']

# Create our framework instance
app = WebFramework()

@app.route('/')
def home(request):
    return f'''
    <h1>Welcome to Our Advanced Framework!</h1>
    <p>Request method: {request.method}</p>
    <p>Request path: {request.path}</p>
    <p>Try: <a href="/user?name=John&age=25">/user?name=John&age=25</a></p>
    <p>Or: <a href="/api/data">/api/data</a> for JSON</p>
    '''

@app.route('/user')
def user_info(request):
    name = request.params.get('name', 'Anonymous')
    age = request.params.get('age', 'Unknown')
    
    return f'''
    <h1>User Information</h1>
    <p>Name: {name}</p>
    <p>Age: {age}</p>
    <p><a href="/">Back to home</a></p>
    '''

@app.route('/api/data')
def api_data(request):
    # Return JSON response
    response = Response()
    return response.json({
        'message': 'Hello from our framework API!',
        'method': request.method,
        'path': request.path,
        'params': request.params
    })

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 8000, app)
    print("Advanced framework running on http://localhost:8000")
    server.serve_forever()

