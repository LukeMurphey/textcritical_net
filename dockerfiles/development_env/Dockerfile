# This Docker image provides a way to run TextCritical.net within a container for development.

# See https://hub.docker.com/_/python
# Django/Python matrix is here: https://docs.djangoproject.com/en/3.0/faq/install/#what-python-version-can-i-use-with-django
FROM python:3.7-slim

RUN apt-get update && apt-get install -y imagemagick calibre ant git curl

# Install node
# See https://askubuntu.com/questions/49390/how-do-i-install-the-latest-version-of-node-js
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt install -y nodejs

# Install yarn (but not "cmdtest")
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install -y yarn

# Change the cache bust value to invalidate the cache so that we get the latest repos
ARG CACHEBUST=2
RUN echo "$CACHEBUST"

# Get the repos
RUN mkdir /git
WORKDIR /git
RUN git clone https://github.com/LukeMurphey/textcritical_net.git
RUN git clone https://github.com/LukeMurphey/textcritical_spa.git

RUN apt-get update && \
             apt-get install -y build-essential && \
             pip install --no-cache-dir -r /git/textcritical_net/src/requirements.txt && \
             apt-get remove -y --purge build-essential && \
             apt-get clean && \
             rm -rf /var/lib/apt/lists/*

# Prep the backend
COPY docker_dev_image_settings.py /git/textcritical_net/src/textcritical/settings.py
COPY dev.local.properties /git/textcritical_net/local.properties
COPY webpack.config.json /git/textcritical_spa/webpack.config.json
# RUN cp /git/textcritical_net/src/textcritical/docker_dev_image_settings.py /git/textcritical_net/src/textcritical/settings.py

# Prep the frontend
WORKDIR /git/textcritical_spa
RUN yarn install

# Expose port 8080 to allow communication to/from the Django server
EXPOSE 8080

# Expose port 8081 to allow communication to/from the Webpack JS server
EXPOSE 8081

# Start the server
COPY entrypoint.sh /git/textcritical_net/dockerfiles/development_env/entrypoint.sh
ENTRYPOINT ["/git/textcritical_net/dockerfiles/development_env/entrypoint.sh"]
