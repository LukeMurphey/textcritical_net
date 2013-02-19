from reader import language_tools
from reader.models import WordDescription
from reader.shortcuts import uniquefy


def description_id_fun(x):
    """
    Provides the string necessary to uniquefy WordDescription instances.
    
    Arguments:
    x -- a word description instance.
    """
    
    return str(x)

def get_word_descriptions( word, ignore_diacritics=False ):
    """
    Gets a list of WordDescription instances for the given word form.
    
    Arguments:
    word -- The word to return WordDescription instances for
    ignore_diacritics -- Indicates if diacritical marks should be ignored for the purposes of matching.
    """
    
    # Do a search for the parse
    word_lookup = language_tools.normalize_unicode( word.lower() )
    
    # If the lookup for the word failed, try doing a lookup without the diacritics
    if ignore_diacritics:
        word_lookup = language_tools.strip_accents(word_lookup)
        descriptions = WordDescription.objects.filter( word_form__basic_form=word_lookup )
    
    else:
        descriptions = WordDescription.objects.filter( word_form__form=word_lookup )
        
    # Make the list distinct
    descriptions = uniquefy(descriptions, description_id_fun)
    
    return descriptions

def get_all_related_forms(word, ignore_diacritics=False ):
    """
    Gets a list of WordForm instances that are possibly for the same word as the one provided.
    
    To do this, this function will
    
    1) Get a list of all WordDescription that match the given word.
    2) Get a list of all Lemma instances associated with the WordDescription
    3) For each lemma, get all forms of the lemma entry
    
    Arguments:
    word -- The word to return WordDescription instances for
    ignore_diacritics -- Indicates if diacritical marks should be ignored for the purposes of matching.
    """
    
    # Get all matching word descriptions
    descriptions = get_word_descriptions(word, ignore_diacritics)
    
    lemmas = []
    
    # Get the lemma entries for the descriptions
    for d in descriptions:
        
        if d.lemma not in lemmas:
            lemmas.append(d.lemma)
            
    # Now that we got the lemmas, let's add all word forms for the lemmas
    word_forms = []
    
    for l in lemmas:
        
        # Get the descriptions for the given lemma entry
        matching_descs = WordDescription.objects.filter(lemma=l)
        
        for m in matching_descs:
            if m.word_form not in word_forms:
                word_forms.append( m.word_form )
    
    return word_forms