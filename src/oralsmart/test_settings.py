"""
Django settings for oralsmart E2E testing.
This inherits from the main settings but uses the same database.
"""

from .settings import *

# Use the same database as development for E2E tests
# This way we don't need to recreate database tables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Use the same database file
    }
}

# Keep most settings the same as production for realistic E2E testing
# Just optimize a few things for testing

# Media files for testing
MEDIA_ROOT = BASE_DIR / 'test_media'

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging during tests for cleaner output
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Security settings for testing
DEBUG = True  # Keep debug on for better error messages
ALLOWED_HOSTS = ['*']

# Cache settings for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Static files for testing
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Password hashers - use faster hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast for testing only
]
