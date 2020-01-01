#!/bin/bash
cd /usr/src/app
mkdir -p /usr/src/app/var/log/

$STATIC_DIR=/static

deploy_static() {
    # Ensure that the static directory was declared
    if [ -d $STATIC_DIR ]
    then
        # Copy over the files if it was
        cp -r /usr/src/app/media/font $STATIC_DIR/media
        cp -r /usr/src/app/media/images $STATIC_DIR/media
        cp -r /usr/src/app/media/javascripts $STATIC_DIR/media
        cp -r /usr/src/app/media/static $STATIC_DIR/media
        cp -r /usr/src/app/media/stylesheets $STATIC_DIR/media
        cp -r /usr/src/app/media/templates $STATIC_DIR/media
        cp /usr/src/app/reader/templates/503.html $STATIC_DIR
    fi
}

deploy_static
python run_server.py