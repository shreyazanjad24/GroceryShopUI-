import os
import sys

# Ensure root directory is in Python path for Vercel serverless execution
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

def handler(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path in ['/api/index', '/api/index/', '/api', '/api/']:
        environ['PATH_INFO'] = '/'
    elif path.startswith('/api/index/'):
        environ['PATH_INFO'] = path[len('/api/index'):]
    elif path.startswith('/api/'):
        environ['PATH_INFO'] = path[len('/api'):]
    return app(environ, start_response)
