# This Docker image provides a way to run TextCritical.net within a container for development.

# See https://hub.docker.com/_/python
# Django/Python matrix is here: https://docs.djangoproject.com/en/3.0/faq/install/#what-python-version-can-i-use-with-django
FROM python:3.8-slim

RUN apt-get update && apt-get install -y imagemagick calibre ant git curl

# Install node
# We are going to use node 16 by registering nodesource so that we have more options to install
# Run the following to see the available versions: apt list -a nodejs
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_16.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update
RUN apt-get install -y nodejs=16.20.2-1nodesource1

# Install yarn (but not "cmdtest")
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install -y yarn

RUN apt-get update && \
             apt-get install -y build-essential && \
             pip install --no-cache-dir -r /workspace/src/requirements.txt && \
             apt-get remove -y --purge build-essential && \
             apt-get clean && \
             rm -rf /var/lib/apt/lists/*

# Prep the backend
#COPY dockerfiles/development_env/docker_dev_image_settings.py /git/textcritical_net/src/textcritical/settings.py
#COPY dockerfiles/development_env/dev.local.properties /git/textcritical_net/local.properties
#COPY dockerfiles/development_env/webpack.config.json /git/textcritical_spa/webpack.config.json
#COPY .devcontainer/entrypoint.sh /bin/entrypoint.sh

# Prep the frontend
#WORKDIR /git/textcritical_net/submodules/textcritical_spa
#RUN yarn install

# Expose port 8080 to allow communication to/from the Django server
EXPOSE 8080

# Expose port 8081 to allow communication to/from the Webpack JS server
EXPOSE 8081

# Start the server
#RUN chmod 755 /bin/entrypoint.sh
ENTRYPOINT ["workspace/entrypoint.sh"]
