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
#
# You can see the app logs using the following command:
#
#       tail /usr/src/app/var/log/app.log
#
# If you run into an issue of not having space, consider pruning. Something like this:
#
#       docker system prune

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
RUN mkdir -p /usr/src/app/
RUN mkdir -p /usr/src/app/var/
RUN mkdir -p /db
COPY src /usr/src/app

# Copy over the Docker settings file
COPY src/textcritical/docker_image_settings.py /usr/src/app/textcritical/settings.py

# Create the necessary directories
RUN mkdir -p /usr/src/app/var/log/
RUN mkdir -p /usr/src/app/var/indexes
RUN mkdir -p /usr/src/app/media/files/
RUN mkdir -p /usr/src/app/var/cache

# Install Kindlgen
RUN apt-get install -y wget
RUN wget http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz -P /bin
RUN tar -C /bin -xf /bin/kindlegen_linux_2.6_i386_v2_9.tar.gz

# Collect the static files
RUN python /usr/src/app/manage.py collectstatic --noinput

# Create a default admin user
#RUN python /usr/src/app/manage.py migrate
#RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'changeme')" | python /usr/src/app/manage.py shell

# EXPOSE port 8080 to allow communication to/from the Django server
EXPOSE 8080

# Start the server
ENTRYPOINT ["/usr/src/app/run_server_docker.sh"]
