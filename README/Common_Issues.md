# Common Errors

## Cannot load works due to error "django.db.utils.OperationalError: no such table: reader_worddescription"

Update src/textcritical/settings.py to use an absolute path to the database files. For example, here is one that overrides the default settings to use an absolute path:

```
from textcritical.default_settings import *

# DATABASE_ROUTERS = []

DATABASES['default']['NAME'] = '/home/luke/git/textcritical_net/var/text_critical.sqlite'
DATABASES['library']['NAME'] = '/home/luke/git/textcritical_net/var/library.sqlite'
```

## Various errors when trying to setup the Python environment

You will need to run PIP to install the requirements from the requirements.txt` in the `src` directory:

```pip3 install -r requirements.txt```

### "c/_cffi_backend.c:15:10: fatal error: ffi.h: No such file or directory"

```apt install libffi-dev```

### "This package requires Rust >=1.41.0."

Install Rust with this:
```curl https://sh.rustup.rs -sSf | sh```

Then run 
```sudo pip3 install -U pip```


### Social authentication fails after upgrading

This may be beause the database needs to be migrated. Run the following to migrate the database:

```
python3 manage.py migrate
```

## Social login is not working

Local authentication will only work the TextCritical or localhost domains. You will also need to use a remote instance of TextCritical to avoid getting a CSRF token failure.
