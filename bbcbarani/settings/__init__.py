"""
Settings package for Bible Baptist Church Barani CMS
"""

# Determine which settings module to use based on environment
import os

# Default to development settings
settings_module = 'bbcbarani.settings.dev'

# Check for environment variable
if 'DJANGO_SETTINGS_MODULE' in os.environ:
    settings_module = os.environ['DJANGO_SETTINGS_MODULE']
elif os.environ.get('ENVIRONMENT') == 'production':
    settings_module = 'bbcbarani.settings.prod'

# Import the appropriate settings
if 'prod' in settings_module:
    from .prod import *
elif 'test' in settings_module:
    from .test import *
else:
    from .dev import *
