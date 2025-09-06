"""
Development settings for Bible Baptist Church Barani CMS

This file contains settings specific to the development environment.
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',  # Useful development tools
]

# Add debug toolbar for development
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE = [
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        ] + MIDDLEWARE

        # Debug toolbar configuration
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
            'SHOW_COLLAPSED': True,
        }

        INTERNAL_IPS = [
            '127.0.0.1',
            'localhost',
        ]
    except ImportError:
        pass

# Database configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'bbcbarani_dev'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET foreign_key_checks = 1;",
        },
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files configuration for development
STATICFILES_DIRS += [
    # Add any additional static directories for development
]

# Media files configuration for development
MEDIA_ROOT = BASE_DIR / 'media_dev'

# Cache configuration for development (use dummy cache or simple Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'bbcbarani-dev-cache',
    }
}

# Disable CORS in development
CORS_ALLOW_ALL_ORIGINS = True

# Development-specific logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Django extensions configuration
if 'django_extensions' in INSTALLED_APPS:
    SHELL_PLUS_IMPORTS = [
        'from django.contrib.auth import get_user_model',
        'User = get_user_model()',
    ]

# Disable some security features for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Development-specific Django REST Framework settings
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',  # For development browsing
]

# Test data generation settings
GENERATE_TEST_DATA = True
TEST_DATA_COUNT = {
    'users': 10,
    'blog_posts': 20,
    'events': 15,
    'ministries': 8,
    'prayer_requests': 25,
}

# Development profiling
if os.environ.get('ENABLE_PROFILING') == 'True':
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
    INSTALLED_APPS += ['silk']

print("🔧 Development settings loaded")
