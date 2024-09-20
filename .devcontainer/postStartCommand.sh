#!/bin/sh

git submodule update --init
cd /workspace/submodules/textcritical_spa

pip install --no-cache-dir -r /workspace/src/requirements.txt

# Copy over the settings file
#cp /workspace/.devcontainer/settings.py /workspace/src/textcritical/

# Copy the properties file
#cp /workspace/dockerfiles/development_env/dev.local.properties /workspace/local.properties

yarn install
yarn run start_listen_all
