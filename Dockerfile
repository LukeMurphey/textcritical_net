# This Docker image provides a way to run TextCritical.net within a container.
# To use this, first build the container:
#
#       docker build -t textcritical .
#
# Next, run the server (on port 8080):
#
#       docker run -p 8080:8080 textcritical
#
# If you need to operate the shell, do it this way:
# 
#       docker run -it --entrypoint /bin/bash textcritical

FROM python:2-slim

# These are copied from python:2-onbuild (https://github.com/tomologic/docker-python/blob/master/2-onbuild/Dockerfile)
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY src/requirements.txt /usr/src/app/
RUN  apt-get update && \
             apt-get install -y build-essential && \
             pip install --no-cache-dir -r requirements.txt && \
             apt-get remove -y --purge build-essential && \
             apt-get clean && \
             rm -rf /var/lib/apt/lists/*

# RUN apt-get install -y libmagickwand-dev
RUN apt-get update && \
             apt-get install -y imagemagick

# Now copy in the textcritical files
COPY src /usr/src/app
COPY var /usr/src/app/var

# EXPOSE port 8080 to allow communication to/from the Django server
EXPOSE 8080

# Start the server
ENTRYPOINT ["/usr/src/app/run_server_docker.sh"]