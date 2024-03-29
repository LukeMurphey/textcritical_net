#!/bin/sh

#Note: this file must use LF, not CR-LF

cd /usr/src/app
mkdir -p /usr/src/app/var/log/

STATIC_DIR="/static"

deploy_static() {
    # Ensure that the static directory was declared
    if [ -d $STATIC_DIR ]
    then
        # Copy over the files
        mkdir -p $STATIC_DIR/media
        cp -r /usr/src/app/media/* $STATIC_DIR/media
        cp /usr/src/app/reader/templates/503.html $STATIC_DIR/
        echo "Done copying files to static"
    fi
}

deploy_static
python run_server.py
