"""
Development settings for Bible Baptist Church CMS
"""
from .base import *

# Development overrides
DEBUG = True
ALLOWED_HOSTS = ['*']

# Use console email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use simple static files storage for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Disable HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

print("🔧 Development mode: DEBUG=True, simple static files")
