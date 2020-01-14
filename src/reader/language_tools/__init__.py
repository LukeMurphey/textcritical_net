from reader.language_tools.greek import Greek
import unicodedata

def transform_text(text, language, return_as_unicode=False):
    """
    Convert the content according to the rules necessary to make the content work for the given language.
    
    Arguments:
    text -- the text to convert
    language -- the language to use for applying the conversion rules
    return_as_unicode -- indicates if the content returned ought to be Unicode instead of a string
    """
    
    # Don't try to process a null string as this will fail
    if text is None:
        return None
    
    # If the language is none, then don't do anything
    if language is None:
        return text
    
    # Convert Greek beta code
    elif language.lower() == "greek":
        text_unicode = Greek.beta_code_to_unicode(text)
        
        if return_as_unicode:
            return text_unicode
        else:
            return text_unicode.encode('utf-8')
    
    # By default, just return the text
    else:
        return text
    
def normalize_unicode(s):
    return unicodedata.normalize("NFKC", s)
    
def strip_accents(s):
    """
    Remove accents from the provided unicode string.
    
    Arguments:
    s -- unicode string to remove accents from.
    """
    
    nkfd_form = unicodedata.normalize('NFKD', s)
    
    stripped_form = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    
    return normalize_unicode(stripped_form)
    #return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def strip_accents_str(s):
    """
    Remove accents from the provided string.
    
    Arguments:
    s -- String to remove accents from.
    """
    
    return strip_accents(s.decode("UTF-8"))