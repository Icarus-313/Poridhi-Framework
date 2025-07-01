# test_framework.py
import unittest
from io import StringIO
import sys
from template_framework import app

class TestClient:
    """Test client for our framework"""
    def __init__(self, app):
        self.app = app
    
    def get(self, path, **kwargs):
        """Simulate a GET request"""
        return self._request('GET', path, **kwargs)
    
    def post(self, path, **kwargs):
        """Simulate a POST request"""
        return self._request('POST', path, **kwargs)
    
    def _request(self, method, path, **kwargs):
        """Simulate any HTTP request"""
        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': kwargs.get('query_string', ''),
            'CONTENT_TYPE': kwargs.get('content_type', ''),
            'CONTENT_LENGTH': str(len(kwargs.get('data', ''))),
            'wsgi.input': StringIO(kwargs.get('data', '')),
        }
        
        # Capture response
        response_data = []
        status = None
        headers = None
        
        def start_response(status_string, headers_list):
            nonlocal status, headers
            status = status_string
            headers = headers_list
        
        # Call the app
        result = self.app(environ, start_response)
        
        # Collect response body
        for chunk in result:
            if isinstance(chunk, bytes):
                response_data.append(chunk.decode('utf-8'))
            else:
                response_data.append(chunk)
        
        return TestResponse(status, headers, ''.join(response_data))

class TestResponse:
    """Response object for testing"""
    def __init__(self, status, headers, data):
        self.status = status
        self.headers = dict(headers) if headers else {}
        self.data = data
        self.status_code = int(status.split()[0])

# Test cases
class FrameworkTests(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        
    def test_home_page(self):
        """Test the home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome to Our Styled Framework', response.data)
    
    def test_custom_route(self):
        """Test our custom test route"""
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Route', response.data)
    
    def test_404_page(self):
        """Test 404 for non-existent pages"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_static_files(self):
        """Test static file serving"""
        response = self.client.get('/static/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/css')
    
    def test_json_response(self):
        """Test JSON responses"""
        response = self.client.get('/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello JSON', response.data)

# Run tests
if __name__ == '__main__':
    # Run the tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Also start the server
    print("\n" + "="*50)
    print("Tests completed! Starting server...")
    print("="*50)