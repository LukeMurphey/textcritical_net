# Deploying TextCritical in Production

## Setting the detault site

You will need to set the default site to match your domain name. Open the administration UI and navigate to the defaul site to change the domain name accordingly.

## Adding social authentication

Social authentication will allow others to store state in TextCritical.net. Follow the below directions to set this up:

1. Create auth provider [in Google](https://django-allauth.readthedocs.io/en/latest/providers.html#google). You may need to make a new project. Note that the client should be under “OAuth 2.0 Client IDs”.
2. Create a [new social app](http://localhost:8080/admin/socialaccount/socialapp/add/) in TextCritical's admin UI.
3. Publish app in Google to make it accessible to the public.
