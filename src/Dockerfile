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

# BTW: This is based upon the instructions at https://semaphoreci.com/community/tutorials/dockerizing-a-python-django-web-application

FROM python:2-onbuild

# EXPOSE port 8080 to allow communication to/from the Django server
EXPOSE 8080

# Start the server
ENTRYPOINT ["/usr/src/app/run_server_docker.sh"]