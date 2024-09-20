This dev container allws you to run TextCritical in a container in order to make development easier.


# Some things you should know
Here are some pointers.

## Where do the database files go?

The database files needs to be in the /var directory

## How do I get the Javascript to use the local server

Copy over the webpack.config.json to tell the development server to not use the remote server (textcritical.net)

```
cp /workspace/dockerfiles/development_env/webpack.config.json /workspace/submodules/textcritical_spa/webpack.config.json
```

# Known issues

## All files in the repo show modifications
This is due to line-ending conversion. What happens is that the files are checked out with CRLF but the development container is running Linux. This causes git to get confused and think the line-endings changed. See https://stackoverflow.com/questions/2517190/how-do-i-force-git-to-use-lf-instead-of-crlf-under-windows

I recommend disabling line-ending conversion on Windows before you checkout the files:

```
git config --global core.autocrlf false
```
