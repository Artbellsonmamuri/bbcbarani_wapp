"""
Test settings for comprehensive testing
"""

from bbcbarani.settings.test import *

# Additional test-specific settings
TESTING = True

# Use faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING_CONFIG = None
import logging
logging.disable(logging.CRITICAL)

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Test file storage
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Disable cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
