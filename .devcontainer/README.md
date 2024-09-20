This dev container allws you to run TextCritical in a container in order to make development easier.

Here are some pointers:

 * The database files needs to be in the /var directory


# Known issues

## All files in the repo show modifications
This is due to line-ending conversion. What happens is that the files are checked out with CRLF but the development container is running Linux. This causes git to get confused and think the line-endings changed. See https://stackoverflow.com/questions/2517190/how-do-i-force-git-to-use-lf-instead-of-crlf-under-windows

I recommend disabling line-ending conversion on Windows before you checkout the files:

```
git config --global core.autocrlf false
```
