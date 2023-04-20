# Deploying TextCritical for Development

I recommend making a development environment in Docker as this is the easiest approach. This document will assume you are using VScode and Docker.

## Start a Docker development environment

Create a new development environment in VSCode that includes Python 3.

## Open ports

Install Portainer in your Docker environment as an Docker extension. Then modify the container to open ports 8080 and 8081. To do this:

1. Open the development container in Portainer
2. Click "Duplicate/Edit"
3. Add new published ports for TCP/8080 and TCP/8081 (this is under the section "Network ports configuration")
4. Deploy the updated container; this will replace the existing container of the same name with a new one with the ports open.

## Copy in library

You need to copy in the library

## Install requirements

    pip3 install -r requirements.txt

## Install other things

    sudo apt-get update
    sudo apt-get install libmagickwand-dev

## Copy settings

Copy the ```default_settings.py``` to ```settings.py``` in ```src/textcritical```. Modify the file accordingly.

## Initialize the textcritical dataebase

    python3 manage.py migrate --database textcritical

# Errors 

## ImportError: MagickWand shared library not found.

This happens when ligmagikwand isn't installed. See "Install other things" above.
