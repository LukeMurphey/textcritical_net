# Django settings for textcritical project.
import os
import django.conf.global_settings as DEFAULT_SETTINGS

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'    : '../var/text_critical.sqlite',# Or path to database file if using sqlite3.
        'USER'    : '',                           # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST'    : '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT'    : '',                           # Set to empty string for default. Not used with sqlite3.
    },
    'library': {
        'ENGINE'  : 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'    : '../var/library.sqlite',      # Or path to database file if using sqlite3.
        'USER'    : '',                           # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST'    : '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT'    : '',                           # Set to empty string for default. Not used with sqlite3.
    }
}

# https://docs.djangoproject.com/en/4.0/releases/3.2/
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Determine if tests are being executed.
import sys
if len(sys.argv) >= 2:
    TESTING = ['manage.py', 'test'] == [os.path.basename(sys.argv[0]), sys.argv[1],]
else:
    TESTING = False

# Setup the database routers that allow the use of works provided in a
# separate database.
if not TESTING:
    DATABASE_ROUTERS = ['textcritical.routers.PreLoadedWorksRouter']

# This is the location where the indexes are located
SEARCH_INDEXES = os.path.join("..", "var", "indexes")

# This website supports page level caching. Uncomment the CACHES setting below and set the LOCATION to being using it
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/opt/webapps/TextCritical.com/var/cache', #Enter the full path to the cache directory here
        'OPTIONS': {
            'MAX_ENTRIES': '30000'
        }
    }
}
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Load CSS and images from a CDN as opposed to using local content
# Note that the content loaded in require 
USE_CDN = True

# Indicates if the sharing buttons (Twitter, Google, LinkedIn, etc) should be included
INCLUDE_SHARING_BUTTONS = True

# Set the name in the admin interface
GRAPPELLI_ADMIN_TITLE = "TextCritical.net"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# This indicates the root of the application and can be used for dynamically configuring directories
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join( os.path.dirname(SITE_ROOT), 'media' ) + '/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# The location to store generated static files
GENERATED_FILES_DIR = os.path.join( MEDIA_ROOT, "files")

# The address and port to use when using the built-in web-server
WEB_SERVER_ADDRESS = '0.0.0.0'  # Use '127.0.0.1' to serve content to localhost only
WEB_SERVER_PORT    = 8080

# Set up the template context processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(SITE_ROOT, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'textcritical.context_processors.global_settings',
                'textcritical.context_processors.get_url_name',
                'textcritical.context_processors.is_async',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

# Indicates whether the dark bootstrap theme ought to be used
USE_DARK_THEME = True

# Indicates whether minified versions of the resources ought to be used if they are available
USE_MINIFIED = True

# Contains the Google analytics ID (optional)
GOOGLE_ANALYTICS_ID = None

# Defines the path to the calibre binary that is used for converting epub files to mobi files. By default, the app assumes that calibre is on the path.
EBOOK_CONVERT = "ebook-convert"

# The following indicates what kind of resource limits are imposed on the search indexer
SEARCH_INDEXER_MEMORY_MB = 128
SEARCH_INDEXER_PROCS = 1

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h6zc9!zhi78yj-8ayt8&amp;f-&amp;!(5d@+fvc75!c(i88^@a*hy9+0y'

MIDDLEWARE = (
    # Uncomment the next line if the hosting web-server doesn't GZIP the responses
    #'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)

ROOT_URLCONF = 'textcritical.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'textcritical.wsgi.application'

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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # social providers
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "auth_success"
ACCOUNT_LOGOUT_ON_GET = True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
