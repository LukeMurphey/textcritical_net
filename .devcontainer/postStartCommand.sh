#!/bin/sh

pip install --no-cache-dir -r /workspace/src/requirements.txt

# Pull the latest for the submodules
# This is commented out because if overrides your own branches
if test -d "/workspace/submodules/"; then
  echo "Submodules already exist"
else
  git submodule update --init
fi

cd /workspace/submodules/textcritical_spa

# Copy over the settings file
cp /workspace/.devcontainer/settings.py /workspace/src/textcritical/

# Copy the properties file
cp /workspace/dockerfiles/development_env/dev.local.properties /workspace/local.properties

# Copy the config for the JS development server so that it links to the local instance
# cp /workspace/dockerfiles/development_env/webpack.config.json /workspace/submodules/textcritical_spa/webpack.config.json

yarn install
yarn run start_listen_all
