# Below is a basic settings file.
# Copy this to settings.py and edit as necessary for your installation
#
# See http://lukemurphey.net/projects/ancient-text-reader/wiki/SetupAndInstall

# Import the default settings so the you do not have to redefine everything
from textcritical.default_settings import *

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'    : '/db/text_critical.sqlite',# Or path to database file if using sqlite3.
        'USER'    : '',                           # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST'    : '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT'    : '',                           # Set to empty string for default. Not used with sqlite3.
    },
    'library': {
        'ENGINE'  : 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'    : '/db/library.sqlite',      # Or path to database file if using sqlite3.
        'USER'    : '',                           # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST'    : '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT'    : '',                           # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = False

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
     'django.contrib.admindocs',
     'django.contrib.humanize',
     'reader'
)

if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/usr/src/app/var/cache',
            'OPTIONS': {
                'MAX_ENTRIES': '3000'
            }
        }
    }

# Define where the media will be served from.
MEDIA_URL = '/media/'

# Define the absolute path to the media on the file-system
MEDIA_ROOT = '/usr/src/app/media/'

STATIC_ROOT = '/usr/src/app/media/static/'

# Define the path to the static directory so that the admin page works
STATIC_URL = '/media/static/'

# Define where the search indexes are
SEARCH_INDEXES = '/usr/src/app/var/indexes'

# Use the kindlegen that has been saved to the /bin directory
KINDLEGEN = '/bin/kindlegen'

USE_CDN = False
USE_MINIFIED = False
INCLUDE_SHARING_BUTTONS = False

# Set up logging. Below is a good start (though you may have to change the paths).
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'logging.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler'
        },
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/usr/src/app/var/log/app.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'db': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/usr/src/app/var/log/db.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'loggers': {
        'django.db': {
            'handlers': ['db'],
            'level': 'ERROR',
            'propagate': False,
        },
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Set the domain name to the list of allowed host names
ALLOWED_HOSTS = ['*']
