'''
Created on Sep 2, 2012

@author: Luke
'''

from reader.language_tools import Greek
from reader.models import Lemma, Case, WordForm, WordDescription, Dialect
import re
import logging
from time import time
from django.db import transaction

logger = logging.getLogger(__name__)

class DiogenesImporter():
    
    @classmethod
    def import_file( cls, file_name, return_created_objects=False, start_line_number=None ):
        
        logger.debug("Importing file, file=\"%s\"", file_name )
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        # If we are returning the objects, then initialize an array to store them. Otherwise, intialize the count.
        if return_created_objects:
            objects = []
        else:
            objects = 0
        
        # Initialize a couple more things...
        f = None # The file handle
        line_number = 0 # The line number
        
        try:
            
            # Open the file
            f = open( file_name, 'r')
            
            # Process each line
            for line in f:
                
                # Note the line number we are importing
                line_number = line_number + 1
                
                # If we are importing starting from a particular line number, then skip lines until you get to this point
                if start_line_number is not None and line_number < start_line_number:
                    pass # Skip this line
                
                else:
                    # Import the line
                    obj = cls.import_line(line, line_number)
                    
                    if return_created_objects:
                        if obj is not None:
                            objects.append( obj )
                    else:
                        objects = objects + 1
        finally:
            if f is not None:
                f.close()
                
        logger.info("Import complete, duration=%i", time() - start_time )
            
        return objects

class DiogenesAnalysesImporter(DiogenesImporter):
    """
    The Diogenes analyses importer imports the analyses file (greek-analyses.txt) from the Diogenes project.
    
    The import is broken down into the following steps:
    
    +------+--------------------+-----------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Step |      Function      |     Purpose     |                                                                           Input                                                                            |
    +------+--------------------+-----------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |    1 | parse_entry        | Get the form    | a(/bra  {537850 9 a(/bra_,a(/bra   favourite slave   fem nom/voc/acc dual}{537850 9 a(/bra_,a(/bra   favourite slave  fem nom/voc sg (attic doric aeolic)} |
    |    2 | parse_descriptions | Parse the forms | {537850 9 a(/bra_,a(/bra   favourite slave   fem nom/voc/acc dual}{537850 9 a(/bra_,a(/bra   favourite slave  fem nom/voc sg (attic doric aeolic)}         |
    |    3 | parse_description  | Parse the form  | {537850 9 a(/bra_,a(/bra   favourite slave   fem nom/voc/acc dual}                                                                                         |
    +------+--------------------+-----------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
    
    The import process consists of populating a series of models. The hierarchy looks something like:
    
        WordForm
         |- WordDescription -> Lemma
             |- Case
    
    """
    
    PARSE_FIND_ATTRS = re.compile("[a-zA-Z0-9_]+")
    
    PARSE_ANALYSIS_DESCRIPTIONS_RE = re.compile("([{][^{]*)")
    PARSE_ANALYSIS_DESCRIPTION_RE = re.compile("(?P<reference_number>[0-9]+)\s+(?P<second_number>[0-9]+)\s+(?P<form_1>[^,\s]+)(,(?P<form_2>[^,\s]+))?\t(?P<definition>.+)\t(?P<attrs>[^}]*)}(\[(?P<extra>[0-9]+)\])?")
        
    @classmethod
    @transaction.commit_on_success
    def import_line(cls, entry, line_number):
        """
        Parse an entry in the Diogenes greek-analyses.txt file.
        
        Example: 'ch/nta    {10100899 9 e)ch/nta_,e)k-a)nta/w    come opposite to    imperf ind act 3rd sg (attic epic ionic)}[32695571]
        
        Arguments:
        entry -- A line in the greek-analysis file
        line_number -- The line number associated with the entry
        """
        
        # Get the form
        beta_code_string = entry[0:entry.find("\t")]
        
        # Strip off the leading exclamation mark which isn't necessary from what I can tell
        if beta_code_string[0] == "!":
            beta_code_string = beta_code_string[1:]
        
        # Find the lemma entry
        greek_code_string = Greek.beta_code_to_unicode(beta_code_string)
        
        # Make the form
        word_form = WordForm()
        word_form.form = greek_code_string
        word_form.save()
        
        # Make the descriptions
        form_number = 0
        
        for desc in cls.PARSE_ANALYSIS_DESCRIPTIONS_RE.findall(entry):
            form_number = form_number + 1
            DiogenesAnalysesImporter.import_analysis_entry(desc, word_form, line_number, form_number)
        
        # Log the line
        if (line_number % 1000) == 0:
            logger.info("Importation progress, line_number=%i", line_number )
        
        return word_form
            
    @classmethod
    def import_analysis_entry(cls, desc, word_form, line_number=None, form_number=None ):
        """
        Import an entry from the Diogenes lemmata file.
        
        Arguments:
        cls -- The base case
        desc -- A string with the part of the line that describes the given form (e.g. "{537850 9 a(/bra_,a(/bra    favourite slave    fem nom/voc/acc dual}")
        word_form -- The WordForm instance associated with the description
        line_number -- The line number that this entry is found on
        form_number -- The number of the form on this line (since each line can have several forms)
        """
        
        # Parse the description
        r = cls.PARSE_ANALYSIS_DESCRIPTION_RE.search(desc)
        
        # Stop if the regex did not match
        if r is None:
            logger.warn("Analysis entry does not match the regex, form=%s, line_number=%r, form_number=%r" % (word_form.form, line_number, form_number) )
            return
        
        d = r.groupdict()
        
        # Find the entry associated by the reference number
        reference_number = d['reference_number']
        lemma = Lemma.objects.filter(reference_number=reference_number)
        
        # Stop if we couldn't find a matching lemma
        if lemma.count() == 0:
            logger.warn("Unable to find the lemma for an analysis entry, form=%s, line_number=%i, form_number=%i" % (word_form.form, line_number, form_number) )
        
        else:
            lemma = lemma[0]
            
            # Add the description of the form
            word_description = WordDescription(description=desc)
            word_description.word_form = word_form
            word_description.lemma = lemma
            word_description.meaning = d['definition']
            
            # Parse into a list of attributes
            attrs = DiogenesLemmataImporter.PARSE_FIND_ATTRS.findall(d['attrs'])
        
            # Update the word description with the data from the attributes
            return DiogenesLemmataImporter.create_description_attributes(attrs, word_description, line_number)

class DiogenesLemmataImporter():
    """
    The Diogenes Lemmata importer imports the lemmata file (greek-lemmata.txt) from the Diogenes project.
    
    The import is broken down into the following steps:
    
    +------+--------------------+----------------------------------------------------------+------------------------------------------------------------------------------+
    | Step |      Function      |                         Purpose                          |                                    Input                                     |
    +------+--------------------+----------------------------------------------------------+------------------------------------------------------------------------------+
    |    1 | parse_lemmata      | Get the reference number and lexical form                | a(dino/s     1892232    a(dina/ (neut nom/voc/acc pl) (fem nom/voc/acc dual) |
    |    2 | parse_form         | Parse the particular form                                | a(dina/ (neut nom/voc/acc pl) (fem nom/voc/acc dual)                         |
    |    3 | parse_descriptions | Parse all possible morphologies associated with the form | (neut nom/voc/acc pl) (fem nom/voc/acc dual)                                 |
    |    4 | parse_description  | Parse each possible morphology associated with the form  | (neut nom/voc/acc pl)                                                        |
    +------+--------------------+----------------------------------------------------------+------------------------------------------------------------------------------+
    
    The import process consists of populating a series of models. The hierarchy looks something like:
    
        Lemma
         |- WordForm
             |- WordDescription
                |- Case
    
    """
    
    PARSE_FORM_RE = re.compile("([^ ]*) (.*)")
    PARSE_DESCRIPTIONS_RE = re.compile("([^ ]*) (.*)")
    
    PARSE_FIND_ATTRS = re.compile("[a-zA-Z0-9_]+")
    
    CASE_MAP = {
                'nom'     : 'nominative',
                'voc'     : 'vocative',
                'acc'     : 'accusative',
                'dat'     : 'dative',
                'gen'     : 'genitive'
                }
    
    TENSE_MAP = {
                'aor'     : 'aorist',
                'pres'    : 'present',
                'imperf'  : 'imperfect',
                'fut'     : 'future',
                'perf'    : 'perfect',
                'futperf' : 'future perfect',
                'plup'    : 'pluperfect'
                }
    
    GENDER_MAP = {
                'fem'     : WordDescription.FEMININE,
                'masc'    : WordDescription.MASCULINE,
                'neut'    : WordDescription.NEUTER
                }
    
    NUMBER_MAP = {
                'sg'      : WordDescription.SINGULAR,
                'dual'    : WordDescription.DUAL,
                'pl'      : WordDescription.PLURAL
                }
    
    PERSON_MAP = {
                '1st'     : WordDescription.FIRST,
                '2nd'     : WordDescription.SECOND,
                '3rd'     : WordDescription.THIRD
                }
    
    MOOD_MAP = {
                "subj"    : "subjunctive",
                "ind"     : "indicative",
                "imperat" : "imperative",
                "opt"     : "optative",
                "interrog": "interrogative"
                }
    
    VOICE_MAP = {
                "mid"     : WordDescription.MIDDLE,
                "pass"    : WordDescription.PASSIVE,
                "act"     : WordDescription.ACTIVE,
                "mp"      : WordDescription.MIDDLE_PASSIVE
                }
    
    PARTS_OF_SPEECH_MAP = {
                           "conj" : WordDescription.CONJUNCTION,
                           "prep" : WordDescription.PREPOSITION
                           }
        
    CLITIC_MAP = {
                  "proclitic" : WordDescription.PROCLITIC,
                  "enclitic" : WordDescription.ENCLITIC
                  }
        
    cached_cases = None
    cached_dialects = None
    
    @staticmethod
    @transaction.commit_on_success
    def parse_lemma( entry, line_number=None ):
        """
        Parse an entry in the Diogenes greek-lemmata.txt file.
        
        Example: 'ch/nta    {10100899 9 e)ch/nta_,e)k-a)nta/w    come opposite to    imperf ind act 3rd sg (attic epic ionic)}[32695571]
        
        Arguments:
        entry -- A line in the greek-lemmata file
        line_number -- The line number associated with the entry
        """
        
        split_entry = entry.split("\t")
        
        lexical_form = Greek.beta_code_str_to_unicode(split_entry[0])
        reference_number = int(split_entry[1])
        
        # Make the entry
        lemma = Lemma(language="Greek")
        lemma.lexical_form = lexical_form
        lemma.reference_number = reference_number
        lemma.save()
        
        """
        # Attach the forms
        forms_raw = split_entry[2:]
        
        for f in forms_raw:
            DiogenesLemmataImporter.parse_form(f, lemma, line_number)
        
        return lemma
        """
    
    @staticmethod
    def parse_form( form, lemma, line_number=None ):
        """
        Parse one of the forms for a lemma.
        
        Example: a(dina/ (neut nom/voc/acc pl) (fem nom/voc/acc dual)
        
        Arguments:
        form -- A string representing a particular form of a lemma
        lemma -- Lemma that is associated with the form
        line_number -- The line number associated with the entry
        """
        
        r = DiogenesLemmataImporter.PARSE_FORM_RE.search(form)
        form, descriptions_str = r.groups()
        
        # Make the form
        word_form = WordForm()
        word_form.lemma = lemma
        word_form.form = Greek.beta_code_str_to_unicode(form)
        word_form.save()
        
        # Add each description of the form
        DiogenesLemmataImporter.parse_descriptions(descriptions_str, word_form, line_number)
        
        return word_form
    
    @staticmethod
    def parse_descriptions( descriptions, word_form, line_number=None, return_created_descriptions=False ):
        """
        Parse descriptions for a particular form.
        
        Example: (neut nom/voc/acc pl) 
        
        Arguments:
        descriptions -- A string containing a series of descriptions; e.g. (neut nom/voc/acc pl) (fem nom/voc/acc dual)
        word_form -- An instance word form that the descriptions are for
        line_number -- The line number associated with the entry
        """
        
        parsed_descriptions = DiogenesLemmataImporter.split_descriptions(descriptions)
        descriptions = []
        
        for d in parsed_descriptions:
            
            desc = DiogenesLemmataImporter.parse_description(d, word_form, line_number=line_number)
            
            if return_created_descriptions:
                descriptions.append( desc )
            
        if return_created_descriptions:
            return descriptions
    
    @staticmethod
    def split_descriptions( description_str ):
        """
        Split descriptions into a list with each description an item in a row.
        
        Example: (neut nom/voc/acc pl) (fem nom/voc/acc dual)
        
        Arguments:
        description_str -- A list of descriptions; e.g. (neut nom/voc/acc pl) (fem nom/voc/acc dual)
        """
        
        current_desc = ""
        depth = 0
        descriptions = []
        
        for c in description_str:
            
            if c =="(":
                depth = depth + 1
                current_desc = current_desc + c
                
            elif c == ")" and depth <= 1:
                depth = depth - 1
                current_desc = current_desc + c
                descriptions.append(current_desc)
                current_desc = ""
                
            elif c == ")":
                depth = depth - 1
                current_desc = current_desc + c
                
            else:
                current_desc = current_desc + c
                
        return descriptions
    
    @staticmethod
    def get_case( case ):
        """
        Get a case associated with the provided string.
        
        Arguments:
        case -- A name of a case.
        """
        
        if DiogenesLemmataImporter.cached_cases is None:
            DiogenesLemmataImporter.cached_cases =  Case.objects.all()
            
        for c in DiogenesLemmataImporter.cached_cases:
            
            if c.name == case:
                return c
            
        # Create the new case
        new_case = Case(name=case)
        new_case.save()
            
        DiogenesLemmataImporter.cached_cases = None
            
        return new_case
    
    @staticmethod
    def get_dialect( dialect ):
        """
        Get a dialect associated with the provided string.
        
        Arguments:
        dialect -- A name of a dialect.
        """
        
        if DiogenesLemmataImporter.cached_dialects is None:
            DiogenesLemmataImporter.cached_dialects =  Dialect.objects.all()
            
        for c in DiogenesLemmataImporter.cached_dialects:
            
            if c.name == dialect:
                return c
            
        # Create the new diallect
        new_dialect = Dialect(name=dialect)
        new_dialect.save()
            
        DiogenesLemmataImporter.cached_dialects = None
            
        return new_dialect
    
    @staticmethod
    def set_part_of_speech( word_description, part_of_speech, raise_if_already_set=True, dont_set_if_already_set=True):
        """
        Set the part of speech.
        
        Arguments:
        word_description -- The word description instance to modify
        part_of_speech -- The part of speech to set
        raise_if_already_set -- Raise an exception if the part of speech was already set to something else
        dont_set_if_already_set -- If the part of speech was already set, then leave the existing value
        """
        
        if word_description.part_of_speech is not None and word_description.part_of_speech != part_of_speech and part_of_speech and raise_if_already_set:
            raise Exception("Part of speech was unexpected, is %i but was set to %i" % ( word_description.part_of_speech, part_of_speech) )
        
        if dont_set_if_already_set and word_description.part_of_speech is not None:
            pass
        
        else:
            word_description.part_of_speech = part_of_speech
    
    @staticmethod
    def parse_description( entry, word_form, raise_on_unused_attributes=False, line_number=None ):
        """
        Parse a description of a word.
        
        Arguments:
        entry -- A string containing a . e.g. (neut nom/voc/acc pl)
        word_form -- The form associated with this description.
        raise_on_unused_attributes -- Raise an exception if an attribute is observed this is not recognized.
        line_number -- The line number for the particular description
        """
        
        # Strip off the parentheses and extra whitespace
        entry = entry.strip()
        
        if entry[0] == "(" and entry[-1] == ")":
            entry = entry[1:-1]
        
        # Parse into a list of attributes
        attrs = DiogenesLemmataImporter.PARSE_FIND_ATTRS.findall(entry)
        
        # This is the word description we are populating
        word_description = WordDescription(description=entry)
        word_description.word_form = word_form
        
        return DiogenesLemmataImporter.create_description_attributes(attrs, word_description, raise_on_unused_attributes, line_number)
        
    @staticmethod
    def create_description_attributes(attrs, word_description, raise_on_unused_attributes=False, line_number=None ):
        
        dialects = []
        cases = []
        
        # Go through the attributes and initialize the instance
        for a in attrs:
            
            # Handle gender
            if a in DiogenesLemmataImporter.GENDER_MAP:
                word_description.gender = DiogenesLemmataImporter.GENDER_MAP[a]
                DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.NOUN)
            
            # Handle number
            elif a in DiogenesLemmataImporter.NUMBER_MAP:
                word_description.number = DiogenesLemmataImporter.NUMBER_MAP[a]
            
            # Handle dialects
            elif a in ["attic", "doric", "aeolic", "epic", "ionic", "homeric", "parad_form", "prose"]:
                dialects.append( DiogenesLemmataImporter.get_dialect(a) )
                
            # Handle part of speech
            elif a in ["adverb", "adverbial"]:
                DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.ADVERB)
                
            # Handle number
            elif a in ["indeclform", "indecl"]:
                word_description.indeclinable = True
            
            # Handle person
            elif a in DiogenesLemmataImporter.PERSON_MAP:
                word_description.person = DiogenesLemmataImporter.PERSON_MAP[a]
            
            # Superlative
            elif a == "superl":
                word_description.superlative = WordDescription.REGULAR
                
            elif a == "irreg_superl":
                word_description.superlative = WordDescription.IRREGULAR
            
            # Comparative
            elif a == "comp":
                word_description.comparative = WordDescription.REGULAR
                
            elif a == "irreg_comp":
                word_description.comparative = WordDescription.IRREGULAR
            
            # Handle tenses
            elif a in DiogenesLemmataImporter.TENSE_MAP:
                word_description.tense = DiogenesLemmataImporter.TENSE_MAP[a]
                DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            # Handle moods
            elif a in DiogenesLemmataImporter.MOOD_MAP:
                word_description.mood = DiogenesLemmataImporter.MOOD_MAP[a]
                DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            elif a == "inf":
                word_description.infinitive = True
                DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            elif a == "part":
                word_description.participle = True
                
            elif a == "expletive":
                word_description.expletive = True
                
            elif a == "poetic":
                word_description.poetic = True
                
            elif a in DiogenesLemmataImporter.PARTS_OF_SPEECH_MAP:
                DiogenesLemmataImporter.set_part_of_speech( word_description, DiogenesLemmataImporter.PARTS_OF_SPEECH_MAP[a] )
                
            elif a == "particle":
                word_description.particle = True
            
            elif a in DiogenesLemmataImporter.CLITIC_MAP:
                word_description.clitic = DiogenesLemmataImporter.CLITIC_MAP[a]
                
            elif a == "nu_movable":
                word_description.movable_nu = True
                
            elif a == "numeral":
                word_description.numeral = True
                
            elif a == "geog_name":
                word_description.geog_name = True
                
            elif a in ["a_priv", "exclam", "iota_intens", "contr", "alphabetic"]:
                pass
            
            elif a in DiogenesLemmataImporter.VOICE_MAP:
                word_description.voice = DiogenesLemmataImporter.VOICE_MAP[a]
                DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            # Handle cases
            elif a in DiogenesLemmataImporter.CASE_MAP:
                cases.append( DiogenesLemmataImporter.get_case(a) )
                DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.NOUN, dont_set_if_already_set=True)
            
            # Warn in the attribute was not processed
            elif raise_on_unused_attributes:
                
                if line_number is not None:
                    raise Exception("Attribute was not expected: attribute=%s, line_number=%i" % (a, line_number) )
                else:
                    raise Exception("Attribute was not expected: attribute=%s" % a )
            
            else:
                
                if line_number is not None:
                    logger.warn("Attribute was not expected: attribute=%s, line_number=%i" % (a, line_number) )
                else:
                    logger.warn("Attribute was not expected: attribute=%s" % a )
        
        # Save the description
        word_description.save()
        
        # Add the cases
        for case in cases:
            word_description.cases.add(case)
            
        # Add the dialects
        for dialect in dialects:
            word_description.dialects.add(dialect)
        
        return word_description
    
    @staticmethod
    def import_file( file_name, return_created_objects=False, start_line_number=None ):
        
        logger.debug("Importing file, file=\"%s\"", file_name )
        
        # Record the start time so that we can measure performance
        start_time = time()
        
        # If we are returning the objects, then initialize an array to store them. Otherwise, intialize the count.
        if return_created_objects:
            lemmas = []
        else:
            lemmas = 0
        
        # Initialize a couple more things...
        f = None # The file handle
        line_number = 0 # The line number
        
        try:
            
            # Open the file
            f = open( file_name, 'r')
            
            # Process each line
            for line in f:
                
                # Note the line number we are importing
                line_number = line_number + 1
                
                # If we are importing starting from a particular line number, then skip lines until you get to this point
                if start_line_number is not None and line_number < start_line_number:
                    pass # Skip this line
                
                else:
                    # Import the line
                    lemma = DiogenesLemmataImporter.parse_lemma(line, line_number)
                    
                    if return_created_objects:
                        lemmas.append( lemma )
                    else:
                        lemmas = lemmas + 1
        finally:
            if f is not None:
                f.close()
                
        logger.info("Import complete, duration=%i", time() - start_time )
            
        return lemmas
    
class DiogenesAnalysesImporterOLD(DiogenesImporter):
    """
    !a/bais    {49671719 9 a_(/bais,h(/bh    youthful prime    fem dat pl (doric)}
    !a/brois    {30699944 9 e)/brois,e)/bros    he-goat    masc dat pl}
    'ch/nta    {10100899 9 e)ch/nta_,e)k-a)nta/w    come opposite to    imperf ind act 3rd sg (attic epic ionic)}[32695571]

    +------+-------------------+---------------------------+-------------------------------------------------------------------------+
    | Step |     Function      |          Purpose          |                                  Input                                  |
    +------+-------------------+---------------------------+-------------------------------------------------------------------------+
    |    1 | parse_analysis    | Get the lexical form      | !a/bais {49671719 9 a_(/bais,h(/bh  youthful prime  fem dat pl (doric)} |
    |    2 | parse_description | Parse the particular form | 49671719 9 a_(/bais,h(/bh  youthful prime  fem dat pl (doric)           |
    +------+-------------------+---------------------------+-------------------------------------------------------------------------+
    """
    
    PARSE_DESCRIPTIONS_RE = re.compile("([{][^{]*)")
    PARSE_DESCRIPTION_RE = re.compile("(?P<reference_number>[0-9]+)\s+(?P<second_number>[0-9]+)\s+(?P<form_1>[^,\s]+)(,(?P<form_2>[^,\s]+))?\t(?P<definition>.+)\t(?P<attrs>[^}]*)}(\[(?P<extra>[0-9]+)\])?")
    PARSE_FIND_ATTRS = re.compile("[a-zA-Z0-9_]+")
    
    @staticmethod
    @transaction.commit_on_success
    def import_line(entry, line_number):
        """
        Parse an entry in the Diogenes greek-analyses.txt file.
        
        Example: 'ch/nta    {10100899 9 e)ch/nta_,e)k-a)nta/w    come opposite to    imperf ind act 3rd sg (attic epic ionic)}[32695571]
        
        Arguments:
        entry -- A line in the greek-analysis file
        line_number -- The line number associated with the entry
        """
        
        # Get the form
        beta_code_string = entry[0:entry.find("\t")]
        
        # Find the lemma entry
        greek_code_string = Greek.beta_code_to_unicode(beta_code_string)
        
        # Make the descriptions
        form_number = 0
        
        for desc in DiogenesAnalysesImporter.PARSE_DESCRIPTIONS_RE.findall(entry):
            form_number = form_number + 1
            DiogenesAnalysesImporter.import_info(desc, greek_code_string, line_number, form_number)
            
    @staticmethod
    def import_info(desc, greek_code_string, line_number=None, form_number=None ):
        related_forms = DiogenesAnalysesImporter.get_related_forms(desc, greek_code_string, line_number)
        
        if related_forms.count() != -1:
            print "Forms discovered, count=%i, line_number=%i, form_number=%i" % (related_forms.count(), line_number, form_number)
    
    @staticmethod
    def get_related_forms(desc, greek_code_string, line_number=None ):
        
        # Parse the description
        r = DiogenesAnalysesImporter.PARSE_DESCRIPTION_RE.search(desc)
        d = r.groupdict()
        
        # Filter the forms to those with the same form
        related_forms = WordDescription.objects.filter(word_form__form=greek_code_string, word_form__lemma__reference_number=d['reference_number'])
        
        # Get the attributes for filtering
        attrs = DiogenesLemmataImporter.PARSE_FIND_ATTRS.findall(d['attrs'])
        
        dialects = []
        cases = []
        
        # Go through the attributes and initialize the instance
        for a in attrs:
            
            # Handle gender
            if a in DiogenesLemmataImporter.GENDER_MAP:
                related_forms = related_forms.filter( gender=DiogenesLemmataImporter.GENDER_MAP[a] )
            
            # Handle number
            elif a in DiogenesLemmataImporter.NUMBER_MAP:
                related_forms = related_forms.filter( number=DiogenesLemmataImporter.NUMBER_MAP[a] )
            
            # Handle dialects
            elif a in ["attic", "doric", "aeolic", "epic", "ionic", "homeric", "parad_form", "prose"]:
                dialects.append( DiogenesLemmataImporter.get_dialect(a) )
                
            # Handle part of speech
            elif a in ["adverb", "adverbial"]:
                related_forms = related_forms.filter( part_of_speech=WordDescription.ADVERB )
                
            # Handle number
            elif a in ["indeclform", "indecl"]:
                related_forms = related_forms.filter( indeclinable=True )
            
            # Handle person
            elif a in DiogenesLemmataImporter.PERSON_MAP:
                related_forms = related_forms.filter( person=DiogenesLemmataImporter.PERSON_MAP[a] )
            
            # Superlative
            elif a == "superl":
                related_forms = related_forms.filter( superlative=WordDescription.REGULAR )
                
            elif a == "irreg_superl":
                related_forms = related_forms.filter( superlative=WordDescription.IRREGULAR )
            
            # Comparative
            elif a == "comp":
                related_forms = related_forms.filter( comparative=WordDescription.REGULAR )
                
            elif a == "irreg_comp":
                related_forms = related_forms.filter( comparative=WordDescription.IRREGULAR )
            
            # Handle tenses
            elif a in DiogenesLemmataImporter.TENSE_MAP:
                related_forms = related_forms.filter( tense=DiogenesLemmataImporter.TENSE_MAP[a] )
                #DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            # Handle moods
            elif a in DiogenesLemmataImporter.MOOD_MAP:
                related_forms = related_forms.filter( mood=DiogenesLemmataImporter.MOOD_MAP[a] )
                #DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            elif a == "inf":
                related_forms = related_forms.filter(infinitive = True)
                #DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            elif a == "part":
                related_forms = related_forms.filter(participle = True)
                
            elif a == "expletive":
                related_forms = related_forms.filter(expletive = True)
                
            elif a == "poetic":
                related_forms = related_forms.filter(poetic = True)
                
            elif a in DiogenesLemmataImporter.PARTS_OF_SPEECH_MAP:
                related_forms = related_forms.filter(part_of_speech = DiogenesLemmataImporter.PARTS_OF_SPEECH_MAP[a])
                
            elif a == "particle":
                related_forms = related_forms.filter(particle = True)
            
            elif a in DiogenesLemmataImporter.CLITIC_MAP:
                related_forms = related_forms.filter(clitic = DiogenesLemmataImporter.CLITIC_MAP[a])
                
            elif a == "nu_movable":
                related_forms = related_forms.filter(movable_nu = True)
                
            elif a == "numeral":
                related_forms = related_forms.filter(numeral = True)
                
            elif a == "geog_name":
                related_forms = related_forms.filter(geog_name = True)
                
            elif a in ["a_priv", "exclam", "iota_intens", "contr"]:
                pass
            
            elif a in DiogenesLemmataImporter.VOICE_MAP:
                related_forms = related_forms.filter(voice = DiogenesLemmataImporter.VOICE_MAP[a])
                #DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.VERB)
            
            # Handle cases
            elif a in DiogenesLemmataImporter.CASE_MAP:
                cases.append( DiogenesLemmataImporter.get_case(a) )
            #    DiogenesLemmataImporter.set_part_of_speech( word_description, WordDescription.NOUN, dont_set_if_already_set=True)
            
        #related_forms = related_forms.filter( 
        
        
        return related_forms
    