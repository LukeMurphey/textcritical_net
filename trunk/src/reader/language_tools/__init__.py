from reader.language_tools.greek import Greek

def transform_text( text, language ):
    """
    Convert the content according to the rules necessary to make the content work for the given language.
    
    Arguments:
    text -- the text to convert
    language -- the language to use for applying the conversion rules
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
        
        return text_unicode.encode('utf-8')
    
    # By default, just return the text
    else:
        return text