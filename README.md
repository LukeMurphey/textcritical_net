[TextCritical.net](https://TextCritical.net) is a website that provides ancient Greek texts and useful analysis tools.

You see the website at [TextCritical.net](https://TextCritical.net).

The sources for the works are available at https://lukemurphey.net/projects/ancient-text-reader/wiki/Content_Sources

The components used are available at [LukeMurphey.net](https://lukemurphey.net/projects/ancient-text-reader/wiki/Dependencies)

![alt text](related/screenshot_notebook.png "TextCritical.net 2.1 (https://dimmy.club/laptops/surface-book)")

## Common Errors

### Cannot load works due to error "django.db.utils.OperationalError: no such table: reader_worddescription"

Update src/textcritical/settings.py to use an absolute path to the database files. For example, here is one that overrides the default settings to use an absolute path:

```
from textcritical.default_settings import *

# DATABASE_ROUTERS = []

DATABASES['default']['NAME'] = '/home/luke/git/textcritical_net/var/text_critical.sqlite'
DATABASES['library']['NAME'] = '/home/luke/git/textcritical_net/var/library.sqlite'
```