from reader.models import Note, UserPreference, NoteReference

class PreLoadedWorksRouter(object):
    """
    A router that allows the use of works that are stored in a separate database. Loading works from a separate database is important
    because the process of importing works is expensive and it can be beneficial to use works in a pre-configured database.
    """
    
    APP_LABEL_READER = "reader"
    DATABASE_NAME_LIBRARY = "library"
    DATABASE_NAME_DEFAULT = "default"

    # Below is a list of models in the reader app that ought to not be sync'd in the library
    MODELS_TO_EXCLUDE = [UserPreference, Note, NoteReference]

    # Build a list of the model names since the names are used by allow_migrate()
    MODEL_NAMES_EXCLUDE = []
    for model in MODELS_TO_EXCLUDE:
        MODEL_NAMES_EXCLUDE.append(model._meta.model_name)
    
    def db_for_read(self, model, **hints):
        
        if model._meta.app_label == PreLoadedWorksRouter.APP_LABEL_READER and model not in self.MODELS_TO_EXCLUDE:
            return PreLoadedWorksRouter.DATABASE_NAME_LIBRARY
        
        return PreLoadedWorksRouter.DATABASE_NAME_DEFAULT
    
    def db_for_write(self, model, **hints):
        
        if model._meta.app_label == PreLoadedWorksRouter.APP_LABEL_READER and model not in self.MODELS_TO_EXCLUDE:
            return PreLoadedWorksRouter.DATABASE_NAME_LIBRARY
        
        return PreLoadedWorksRouter.DATABASE_NAME_DEFAULT
    
    def allow_relation(self, obj1, obj2, **hints):
        
        # Allow the relationship if it is for the same app
        if obj1._meta.app_label == obj2._meta.app_label:
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # If this is one of the models for the library database and the reader app then allow the
        # changes unless it is one of the models that we have blacklisted
        if db == PreLoadedWorksRouter.DATABASE_NAME_LIBRARY and app_label == PreLoadedWorksRouter.APP_LABEL_READER and model_name not in self.MODEL_NAMES_EXCLUDE:
            return True

        # If this is neither for the library database and it isn't for the reader app, then allow
        # the changes to the database. This should allow changes to the main database.
        elif db != PreLoadedWorksRouter.DATABASE_NAME_LIBRARY and app_label != PreLoadedWorksRouter.APP_LABEL_READER:
            return True

        # If this is not for the library data and it is for the reader app but is one of the blacklisted
        # models, then allow it.
        elif db != PreLoadedWorksRouter.DATABASE_NAME_LIBRARY and app_label == PreLoadedWorksRouter.APP_LABEL_READER and model_name in self.MODEL_NAMES_EXCLUDE:
            return True
        
        # Don't allow other models (like users) to be sync'd to this database
        else:
            return False
