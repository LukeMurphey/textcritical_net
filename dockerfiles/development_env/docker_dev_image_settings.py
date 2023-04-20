# Below is a basic settings file.
# Copy this to settings.py and edit as necessary for your installation
#
# See http://lukemurphey.net/projects/ancient-text-reader/wiki/SetupAndInstall

# Import the default settings so the you do not have to redefine everything
from textcritical.default_settings import *
import string
import random

SECRET_KEY_LOCATION = '/git/textcritical_net/var/secret.txt'

# Generate or load the secret key
try:
    with open(SECRET_KEY_LOCATION, 'r') as secret_key_file:
        SECRET_KEY = secret_key_file.read()
except:
    # Make a new secret key
    c = string.ascii_letters + string.digits + string.punctuation
    SECRET_KEY = ''.join(random.choice(c) for i in range(67))

    # Write out the secret key
    with open(SECRET_KEY_LOCATION, 'w') as secret_key_file:
        secret_key_file.write(SECRET_KEY)

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'    : '/git/textcritical_net/var/db/text_critical.sqlite',# Or path to database file if using sqlite3.
        'USER'    : '',                           # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST'    : '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT'    : '',                           # Set to empty string for default. Not used with sqlite3.
    },
    'library': {
        'ENGINE'  : 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'    : '/git/textcritical_net/var/db/library.sqlite',      # Or path to database file if using sqlite3.
        'USER'    : '',                           # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST'    : '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT'    : '',                           # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = True

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
    'reader',
    'corsheaders',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # social providers
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
)

if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/git/textcritical_net/var/cache',
            'OPTIONS': {
                'MAX_ENTRIES': '3000'
            }
        }
    }

# Define where the media will be served from.
MEDIA_URL = '/media/'

# Define the absolute path to the media on the file-system
MEDIA_ROOT = '/git/textcritical_net/media/'

STATIC_ROOT = '/git/textcritical_net/media/static/'

# Define the path to the static directory so that the admin page works
STATIC_URL = '/media/static/'

# Define where the search indexes are
SEARCH_INDEXES = '/git/textcritical_net/var/indexes'

# Use the calibre binary that has been saved to the /bin directory
EBOOK_CONVERT = '/usr/bin/ebook-convert'

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
            'class':'logging.StreamHandler',
            'formatter':'standard',
        },
    },
}

# Set the domain name to the list of allowed host names
ALLOWED_HOSTS = ['*']

# Set CORS origin so that API requests can be performed from browers
# CORS_ORIGIN_ALLOW_ALL = True
