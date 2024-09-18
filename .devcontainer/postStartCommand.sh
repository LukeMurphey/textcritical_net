#!/bin/sh

git submodule update --init
cd /workspace/submodules/textcritical_spa

yarn install
yarn run start_listen_all

# Copy over the settings file
cp /workspace/.devcontainer/settings.py /workspace/src/textcritical/

# Copy the properties file
cp /workspace/dockerfiles/development_env/dev.local.properties /workspace/local.properties
