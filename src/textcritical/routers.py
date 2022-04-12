
class PreLoadedWorksRouter(object):
    """
    A router that allows the use of works that are stored in a separate database. Loading works from a separate database is important
    because the process of importing works is expensive and it can be beneficial to use works in a pre-configured database.
    """
    
    APP_LABEL     = "reader"
    DATABASE_NAME = "library"
    
    def db_for_read(self, model, **hints):
        
        if model._meta.app_label == PreLoadedWorksRouter.APP_LABEL:
            return PreLoadedWorksRouter.DATABASE_NAME
        
        return None
    
    def db_for_write(self, model, **hints):
        
        if model._meta.app_label == PreLoadedWorksRouter.APP_LABEL:
            return PreLoadedWorksRouter.DATABASE_NAME
        
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        
        if obj1._meta.app_label == PreLoadedWorksRouter.APP_LABEL or obj2._meta.app_label == PreLoadedWorksRouter.APP_LABEL:
            return True
        
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # If this is one of the models for the library database and the reader app then allow the
        # changes
        if db == PreLoadedWorksRouter.DATABASE_NAME and app_label == PreLoadedWorksRouter.APP_LABEL:
            return True

        # If this is neither for the library database and it isn't for the reader app, then allow
        # the changes to the database. This should allow changes to the main database.
        elif db != PreLoadedWorksRouter.DATABASE_NAME and app_label != PreLoadedWorksRouter.APP_LABEL:
            return True
        
        # Don't allow other models (like users) to be sync'd to this database
        else:
            return False
