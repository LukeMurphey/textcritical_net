#!/bin/bash
cd /usr/src/app
mkdir -p /usr/src/app/var/log/

deploy_static() {
    # Ensure that the static directory was declared
    if [ -d "/media" ]
    then
        # Copy over the files if it was
        cp -r /usr/src/app/media/font /media
        cp -r /usr/src/app/media/images /media
        cp -r /usr/src/app/media/javascripts /media
        cp -r /usr/src/app/media/static /media
        cp -r /usr/src/app/media/stylesheets /media
        cp -r /usr/src/app/media/templates /media
        cp /usr/src/app/reader/templates/503.html /media
    fi
}

deploy_static
python run_server.py