"""
WSGI config for Bible Baptist Church CMS
"""
import os
from django.core.wsgi import get_wsgi_application

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bbcbarani.settings.prod')

application = get_wsgi_application()
