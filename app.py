"""
WSGI compatibility entrypoint for hosting platforms (Render, Heroku, etc.)
that default to 'gunicorn app:app'.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoestore.settings')

app = get_wsgi_application()
application = app
