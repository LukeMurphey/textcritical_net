# Below is a basic settings file.
# Copy this to settings.py and edit as necessary for your installation
#
# See http://lukemurphey.net/projects/ancient-text-reader/wiki/SetupAndInstall

# Import the default settings so the you do not have to redefine everything
from textcritical.default_settings import *

# Define where the media will be served from.
MEDIA_URL = '/media/'

# Define the absolute path to the media on the file-system
MEDIA_ROOT = 'C:/Users/Luke/Workspace/TextCritical.com/src/media/'

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
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler'
        },
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '../var/log/app.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'db': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '../var/log/db.log',
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
ALLOWED_HOSTS = [
    '.textcritical.com',
    '127.0.0.1',
]