from reader.models import UserPreference
class PreLoadedWorksRouter(object):
    """
    A router that allows the use of works that are stored in a separate database. Loading works from a separate database is important
    because the process of importing works is expensive and it can be beneficial to use works in a pre-configured database.
    """
    
    APP_LABEL     = "reader"
    DATABASE_NAME = "library"
    # Below is a list of models in the reader app that ought to not be sync'd in the library
    MODELS_TO_NOT_INCLUDE = [UserPreference]

    # Build a list of the model names since the names are used by allow_migrate()
    MODEL_NAMES_TO_NOT_INCLUDE = []
    for model in MODELS_TO_NOT_INCLUDE:
        MODEL_NAMES_TO_NOT_INCLUDE.append(model._meta.model_name)
    
    def db_for_read(self, model, **hints):
        
        if model._meta.app_label == PreLoadedWorksRouter.APP_LABEL and model not in self.MODELS_TO_NOT_INCLUDE:
            return PreLoadedWorksRouter.DATABASE_NAME
        
        return None
    
    def db_for_write(self, model, **hints):
        
        if model._meta.app_label == PreLoadedWorksRouter.APP_LABEL and model not in self.MODELS_TO_NOT_INCLUDE:
            return PreLoadedWorksRouter.DATABASE_NAME
        
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        
        if obj1._meta.app_label == PreLoadedWorksRouter.APP_LABEL or obj2._meta.app_label == PreLoadedWorksRouter.APP_LABEL:
            return True
        
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # If this is one of the models for the library database and the reader app then allow the
        # changes unless it is one of the models that we have blacklisted
        if db == PreLoadedWorksRouter.DATABASE_NAME and app_label == PreLoadedWorksRouter.APP_LABEL and model_name not in self.MODEL_NAMES_TO_NOT_INCLUDE:
            return True

        # If this is neither for the library database and it isn't for the reader app, then allow
        # the changes to the database. This should allow changes to the main database.
        elif db != PreLoadedWorksRouter.DATABASE_NAME and app_label != PreLoadedWorksRouter.APP_LABEL:
            return True

        # If this is not for the library data and it is for the reader app but is one of the blacklisted
        # models, then allow it.
        elif db != PreLoadedWorksRouter.DATABASE_NAME and app_label == PreLoadedWorksRouter.APP_LABEL and model_name in self.MODEL_NAMES_TO_NOT_INCLUDE:
            return True
        
        # Don't allow other models (like users) to be sync'd to this database
        else:
            return False
