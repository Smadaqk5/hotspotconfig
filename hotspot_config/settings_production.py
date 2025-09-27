"""
Production settings for GitHub deployment
"""
import os
from .settings import *

# Override settings for production
DEBUG = False
ALLOWED_HOSTS = ['*']  # Allow all hosts for GitHub deployment

# Use environment variables or sensible defaults
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-please')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Use console backend for GitHub

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
