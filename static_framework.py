import os
import mimetypes
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

class Request:
    def __init__(self, environ):
        self.environ = environ
        self.path = environ.get('PATH_INFO', '/')
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.query_string = environ.get('QUERY_STRING', '')
        self.params = self.parse_query_string(self.query_string)
    
    def parse_query_string(self, qs):
        parsed = parse_qs(qs)
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

class Response:
    def __init__(self):
        self.status = '200 OK'
        self.headers = [('Content-Type', 'text/html; charset=utf-8')]
        self.body = b''
    def set_body(self, content):
        if isinstance(content, str):
            self.body = content.encode('utf-8')
        else:
            self.body = content

class Middleware:
    def __init__(self, app):
        self.app = app
        self.middlewares = []
    def add(self, func):
        self.middlewares.append(func)
    def __call__(self, environ, start_response):
        def apply(i, env):
            if i < len(self.middlewares):
                return self.middlewares[i](env, lambda e: apply(i+1, e))
            else:
                return self.app(env, start_response)
        return apply(0, environ)

class StaticFileHandler:
    def __init__(self, static_dir='static', url_prefix='/static/'):
        self.static_dir = os.path.abspath(static_dir)
        self.url_prefix = url_prefix
        os.makedirs(self.static_dir, exist_ok=True)
        self._create_default_css()
    def _create_default_css(self):
        css_path = os.path.join(self.static_dir, 'style.css')
        if not os.path.exists(css_path):
            css = '''
            body { font-family: Arial, sans-serif; background: #f0f0f0; margin:0; padding:20px; }
            .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 8px; }
            .nav { background: #007bff; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .nav a { color: white; margin-right: 20px; text-decoration: none; font-weight: bold; }
            .nav a:hover { text-decoration: underline; }
            '''
            with open(css_path, 'w') as f:
                f.write(css)
    def serve(self, path):
        if not path.startswith(self.url_prefix):
            return None
        rel_path = path[len(self.url_prefix):]
        full_path = os.path.join(self.static_dir, rel_path)
        if not os.path.isfile(full_path):
            return None
        mime, _ = mimetypes.guess_type(full_path)
        mime = mime or 'application/octet-stream'
        with open(full_path, 'rb') as f:
            data = f.read()
        return data, mime

class PoridhiFramework:
    def __init__(self):
        self.routes = {}
        self.static_handler = StaticFileHandler()
        self.middleware = Middleware(self.wsgi_app)
    def route(self, path, methods=['GET']):
        def decorator(func):
            self.routes[(path, tuple(methods))] = func
            return func
        return decorator
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = Response()
        # Static files
        if request.path.startswith(self.static_handler.url_prefix):
            result = self.static_handler.serve(request.path)
            if result:
                data, mime = result
                response.headers = [('Content-Type', mime)]
                response.set_body(data)
                start_response(response.status, response.headers)
                return [response.body]
            else:
                response.status = '404 Not Found'
                response.set_body('<h1>404 Not Found</h1><p>Static file not found.</p>')
                start_response(response.status, response.headers)
                return [response.body]
        # Routes
        handler = None
        for (route_path, methods) in self.routes:
            if route_path == request.path and request.method in methods:
                handler = self.routes[(route_path, methods)]
                break
        if handler:
            try:
                body = handler(request)
                if isinstance(body, Response):
                    response = body
                else:
                    response.set_body(body)
            except Exception as e:
                response.status = '500 Internal Server Error'
                response.set_body(f'<h1>500 Internal Server Error</h1><pre>{e}</pre>')
        else:
            response.status = '404 Not Found'
            response.set_body('<h1>404 Not Found</h1><p>Route not found.</p>')
        start_response(response.status, response.headers)
        return [response.body]
    def add_middleware(self, func):
        self.middleware.add(func)
    def __call__(self, environ, start_response):
        return self.middleware(environ, start_response)
    def render_template(self, template_str, context=None):
        if context is None:
            context = {}
        try:
            return template_str.format(**context)
        except KeyError as e:
            return f"Template error: missing key {e}"

app = PoridhiFramework()

def logging_middleware(environ, next_func):
    method = environ.get('REQUEST_METHOD', '')
    path = environ.get('PATH_INFO', '')
    print(f"[LOG] {method} {path}")
    return next_func(environ)

app.add_middleware(logging_middleware)

@app.route('/')
def home(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Poridhi Framework Home</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a>
                <a href="/features">Features</a>
            </div>
            <h1>Welcome to Poridhi Framework!</h1>
            <p>This is the home page with static CSS and routing.</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/features')
def features(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Features</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a>
                <a href="/features">Features</a>
            </div>
            <h1>Framework Features</h1>
            <ul>
                <li>✅ WSGI Support</li>
                <li>✅ Routing with Decorators</li>
                <li>✅ Middleware Support</li>
                <li>✅ Static File Serving</li>
                <li>✅ Basic Template Rendering</li>
                <li>✅ Request and Response Objects</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    print("Starting Poridhi Framework server at http://localhost:8000")
    with make_server('localhost', 8000, app) as httpd:
        print("Server running... press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")