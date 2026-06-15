import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

# Set environment Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()