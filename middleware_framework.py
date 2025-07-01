# middleware_framework.py
import time
from datetime import datetime
from urllib.parse import parse_qs

class Request:
    def __init__(self, environ):
        self.environ = environ
        self.path = environ['PATH_INFO']
        self.method = environ['REQUEST_METHOD']
        self.query_string = environ.get('QUERY_STRING', '')
        self.params = self.parse_query_string(self.query_string)

    def parse_query_string(self, query_string):
        parsed = parse_qs(query_string)
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

class Response:
    def __init__(self):
        self.status = '200 OK'
        self.headers = [('Content-Type', 'text/html')]
        self.body = ''

class Middleware:
    """Base middleware class"""
    def process_request(self, request):
        """Called before the view handler"""
        pass
    
    def process_response(self, request, response):
        """Called after the view handler"""
        return response

class LoggingMiddleware(Middleware):
    """Logs every request"""
    def process_request(self, request):
        print(f"[{datetime.now()}] {request.method} {request.path}")
        request.start_time = time.time()
    
    def process_response(self, request, response):
        duration = time.time() - getattr(request, 'start_time', time.time())
        print(f"Response took {duration:.3f} seconds")
        return response

class SecurityMiddleware(Middleware):
    """Adds security headers"""
    def process_response(self, request, response):
        # Add security headers
        if hasattr(response, 'headers'):
            response.headers.append(('X-Content-Type-Options', 'nosniff'))
            response.headers.append(('X-Frame-Options', 'DENY'))
        return response

class MiddlewareFramework:
    def __init__(self):
        self.routes = {}
        self.middlewares = []
    
    def add_middleware(self, middleware):
        """Add middleware to the stack"""
        self.middlewares.append(middleware)
    
    def route(self, path):
        def wrapper(handler_func):
            self.routes[path] = handler_func
            return handler_func
        return wrapper
    
    def __call__(self, environ, start_response):
        request = Request(environ)
        
        # Process request through middleware
        for middleware in self.middlewares:
            middleware.process_request(request)
        
        # Handle the request
        if request.path in self.routes:
            try:
                result = self.routes[request.path](request)
                
                # Create response object
                response = Response()
                response.body = result
                
                # Process response through middleware (in reverse order)
                for middleware in reversed(self.middlewares):
                    response = middleware.process_response(request, response)
                
                start_response(response.status, response.headers)
                return [response.body.encode('utf-8')]
                
            except Exception as e:
                start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
                return [f'<h1>Error:</h1><p>{str(e)}</p>'.encode('utf-8')]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b'<h1>404 - Page Not Found</h1>']

# Create app with middleware
app = MiddlewareFramework()
app.add_middleware(LoggingMiddleware())
app.add_middleware(SecurityMiddleware())

@app.route('/')
def home(request):
    return '<h1>Home with Middleware</h1><p>Check your console for logs!</p>'

@app.route('/slow')
def slow_page(request):
    time.sleep(2)  # Simulate slow operation
    return '<h1>Slow Page</h1><p>This took 2 seconds to load.</p>'