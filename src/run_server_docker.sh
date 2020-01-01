#!/bin/bash
cd /usr/src/app
mkdir -p /usr/src/app/var/log/

deploy_static() {
    # Ensure that the static directory was declared
    if [ -d "/media" ]
    then
        # Copy over the files if it was
        cp -r /usr/src/app/media/* /media
    fi
}

deploy_static
python run_server.py