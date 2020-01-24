#!/bin/bash
cd /usr/src/app
mkdir -p /usr/src/app/var/log/

# Run the tests
python manage.py test
