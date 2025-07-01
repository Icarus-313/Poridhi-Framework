# templated_framework.py
import os
import re
from pathlib import Path

class TemplateEngine:
    """Simple template engine similar to Django's"""
    
    def __init__(self, template_dir='templates'):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
    
    def render(self, template_name, context=None):
        """Render a template with context data"""
        if context is None:
            context = {}
        
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            return f"<h1>Template Error</h1><p>Template '{template_name}' not found</p>"
        
        # Read template file
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Simple variable replacement: {{ variable_name }}
        def replace_var(match):
            var_name = match.group(1).strip()
            return str(context.get(var_name, f'{{{{ {var_name} }}}}'))
        
        # Replace variables
        rendered = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_var, template_content)
        
        # Simple for loop: {% for item in items %}...{% endfor %}
        def replace_for_loop(match):
            loop_var = match.group(1).strip()
            list_var = match.group(2).strip()
            loop_content = match.group(3)
            
            if list_var not in context:
                return f"<!-- List '{list_var}' not found in context -->"
            
            result = ""
            for item in context[list_var]:
                # Replace loop variable in content
                item_content = loop_content.replace(f'{{{{ {loop_var} }}}}', str(item))
                result += item_content
            
            return result
        
        # Handle for loops
        rendered = re.sub(
            r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}',
            replace_for_loop,
            rendered,
            flags=re.DOTALL
        )
        
        return rendered

class Request:
    def __init__(self, environ):
        self.environ = environ
        self.path = environ['PATH_INFO']
        self.method = environ['REQUEST_METHOD']
        self.query_string = environ.get('QUERY_STRING', '')
        self.params = self.parse_query_string(self.query_string)

    def parse_query_string(self, query_string):
        from urllib.parse import parse_qs
        parsed = parse_qs(query_string)
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}


class TemplatedFramework:
    def __init__(self, template_dir='templates'):
        self.routes = {}
        self.templates = TemplateEngine(template_dir)
        self.setup_default_templates()
    
    def setup_default_templates(self):
        """Create some default templates"""
        templates_dir = Path('templates')
        templates_dir.mkdir(exist_ok=True)
        
        # Base template
        base_template = '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .nav { background: #f0f0f0; padding: 10px; margin-bottom: 20px; }
        .nav a { margin-right: 15px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/users">Users</a>
        <a href="/about">About</a>
    </div>
    <div class="content">
        {{ content }}
    </div>
</body>
</html>'''
        
        # Home template
        home_template = '''<h1>Welcome to {{ site_name }}!</h1>
<p>This page is rendered using templates.</p>
<p>Current time: {{ current_time }}</p>
<p>We have {{ user_count }} users registered.</p>'''
        
        # Users template
        users_template = '''<h1>Our Users</h1>
<ul>
{% for user in users %}
    <li>{{ user }}</li>
{% endfor %}
</ul>
<p>Total: {{ user_count }} users</p>'''
        
        # Write templates to files
        with open('templates/base.html', 'w') as f:
            f.write(base_template)
        with open('templates/home.html', 'w') as f:
            f.write(home_template)
        with open('templates/users.html', 'w') as f:
            f.write(users_template)
    
    def route(self, path):
        def wrapper(handler_func):
            self.routes[path] = handler_func
            return handler_func
        return wrapper
    
    def render_template(self, template_name, **context):
        """Helper method to render templates with base layout"""
        content = self.templates.render(template_name, context)
        
        # Wrap in base template
        base_context = {
            'title': context.get('title', 'My Framework'),
            'content': content
        }
        
        return self.templates.render('base.html', base_context)
    
    def __call__(self, environ, start_response):
        request = Request(environ)
        
        if request.path in self.routes:
            try:
                result = self.routes[request.path](request, self)
                start_response('200 OK', [('Content-Type', 'text/html')])
                return [result.encode('utf-8')]
            except Exception as e:
                start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
                return [f'<h1>Error:</h1><p>{str(e)}</p>'.encode('utf-8')]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b'<h1>404 - Page Not Found</h1>']

# Create app with templates
app = TemplatedFramework()

@app.route('/')
def home(request, framework):
    from datetime import datetime
    return framework.render_template('home.html',
        title='Home Page',
        site_name='My Awesome Framework',
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        user_count=3
    )

@app.route('/users')
def users(request, framework):
    user_list = ['Alice', 'Bob', 'Charlie']
    return framework.render_template('users.html',
        title='Users',
        users=user_list,
        user_count=len(user_list)
    )

@app.route('/about')
def about(request, framework):
    return framework.render_template('home.html',
        title='About',
        site_name='About Our Framework',
        current_time='Built with Python!',
        user_count=0
    )