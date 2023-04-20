# Setting up a new instance

These instructions will assume you are using Docker to run TextCritical because it is the easiest way to run the app.

## Configuring the databases

TextCritical is setup to support two databases:

1. Library: the library of works (Greek and English)
2. TextCritical: everything else (authentication, etc.)

For development, you can use SQLite for both of them.

### Setting up the library database

For development, you can use [this sample database](https://lukemurphey.net/attachments/download/461/library.sqlite). To use it, place it in `/var/db` (i.e. `var/db/library.sqlite`).

### Setting up the textcritical database

Start the Docker container:

    docker-compose up

Once the container comes up, connect to the container via shell and run the following command:

    python manage.py migrate

This will cause the textcritical to be initialized for you.

Now make the superuser account:

    python manage.py createsuperuser

This will make the superuser account such that you can log in; to do so, go to the http://localhost:8080/admin and log into the administration UI.

## Deploying in production

There are several more things you may wont to do for deploying the app in production. See [Deploying_In_Production.md](Deploying_In_Production.md) for details.