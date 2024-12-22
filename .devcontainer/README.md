This dev container allws you to run TextCritical in a container in order to make development easier.


# Some things you should know
Here are some pointers.

## Where do the database files go?

The database files needs to be in the /var directory

## How do I get the frontend to use the local server?

Copy over the webpack.config.json to tell the development server to not use the remote server (textcritical.net)

```
cp /workspace/dockerfiles/development_env/webpack.config.json /workspace/submodules/textcritical_spa/webpack.config.json
```

# How do I login via the social login (Google)?

You need to make sure to run Django locally. This will require a database file in `/var/text_critical.sqlite` that has been initialized.

Once you have the database file, then run the local server:

```
cd ./workspace/src
python manage.py runserver 0.0.0.0:8080
```

Next, prepare the frontend to use the local server. You can do this by editing the file in `.devcontainer/webpack.config.json` to point to the local server:

```
{
    "endpoint": "local"
}
```

Once this is done, run the frontend code using `.devcontainer/postStartCommand.sh`.

# Issues

## All files in the repo show modifications
This is due to line-ending conversion. What happens is that the files are checked out with CRLF but the development container is running Linux. This causes git to get confused and think the line-endings changed. See https://stackoverflow.com/questions/2517190/how-do-i-force-git-to-use-lf-instead-of-crlf-under-windows

I recommend disabling line-ending conversion on Windows before you checkout the files:

```
git config --global core.autocrlf false
```

## 
