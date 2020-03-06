from wsgiref.simple_server import make_server
import os
import sys

# Setup path constants
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(ROOT_DIR, 'vendor')
STATIC_FILE_DIR = os.path.join(ROOT_DIR, 'static')

# Setup app specific constants
ONE_HOUR = 3600
ONE_DAY = ONE_HOUR * 24
AUTO_REFRESH = os.environ.get('AUTO_REFRESH', False)

# Add vendor dir to PYTHON_PATH
sys.path.append(VENDOR_DIR)

# Import vendored modules
from whitenoise import WhiteNoise  # noqa: E402
import awsgi  # noqa: E402

# Define which binary mime-types should be served as base64 encoded
# This makes serving these types through API Gateway a bit easier
BASE64_CONTENT_TYPES = [
    'image/png', 
    'image/jpg', 
    'image/gif', 
    'font/ttf',
    'application/font-woff',
    'application/font-woff2',
]

# Define any explicit file-extention/mime-type mappings
MIME_TYPES = {
    '.woff': 'application/font-woff',
    '.woff2': 'application/font-woff2',
}

# Define a WSGI application that responds with a 404 error on every request
def application_404(environ, start_response):
    response_body = 'Not Found'
    status = '404 Not Found'
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body))),
    ]
    start_response(status, response_headers)
    return [response_body.encode()]


# Wrap the 404 responder above around a static file handler (Whitenoise)
# This will intercept requests for serve static files and serve them if found
# If not found, it will default to the 404 response
APP = WhiteNoise(
    application_404,
    root=STATIC_FILE_DIR,
    index_file=True,
    mimetypes=MIME_TYPES,
    max_age=ONE_DAY,
    autorefresh=AUTO_REFRESH,
)


# Define the lambda event handler to route all requests through the app above
def lambda_handler(event, context):
    return awsgi.response(APP, event, context, base64_content_types=BASE64_CONTENT_TYPES)


# Define local testing environment:  AUTO_REFRESH=True python app.py
if __name__ == '__main__':
    try:
        port = 8051
        httpd = make_server('localhost', port, APP)
        print('Starting local server')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stopping local server')
