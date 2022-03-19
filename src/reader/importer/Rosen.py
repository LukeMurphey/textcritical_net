from reader.language_tools import Greek
from reader.models import Lemma, Case, WordForm, WordDescription, Dialect
from reader.importer.LineImporter import LineImporter
import re
import logging
from time import time
from django.db import transaction

logger = logging.getLogger(__name__)

# See http://www.mobileread.mobi/forums/showthread.php?t=256360 and https://latin-dict.github.io/dictionaries/morphology-grc.html
class RosenAnalysesImporter(LineImporter):
    """
    Importer for the analyses of words in the Greek language from the file made by Jacob Rosen.
    """
    COMMENT_RE = re.compile("[#].*")
    FORMS_RE = re.compile("[^|]+")
    MAIN_ANALYSIS_RE = re.compile("(.*):(.*):(.*)")
    PARSE_FIND_ATTRS = re.compile("[a-zA-Z0-9_]+")

    CASE_MAP = {
        'nom': 'nominative',
        'voc': 'vocative',
        'acc': 'accusative',
        'dat': 'dative',
        'gen': 'genitive'
    }

    TENSE_MAP = {
        'aor': 'aorist',
        'pres': 'present',
        'imperf': 'imperfect',
        'fut': 'future',
        'perf': 'perfect',
        'futperf': 'future perfect',
        'plup': 'pluperfect'
    }

    NUMBER_MAP = {
        'sg': WordDescription.SINGULAR,
        'dual': WordDescription.DUAL,
        'pl': WordDescription.PLURAL
    }

    PERSON_MAP = {
        '1st': WordDescription.FIRST,
        '2nd': WordDescription.SECOND,
        '3rd': WordDescription.THIRD
    }

    MOOD_MAP = {
        "subj": "subjunctive",
        "ind": "indicative",
        "imperat": "imperative",
        "opt": "optative",
        "interrog": "interrogative"
    }

    VOICE_MAP = {
        "mid": WordDescription.MIDDLE,
        "pass": WordDescription.PASSIVE,
        "act": WordDescription.ACTIVE,
        "mp": WordDescription.MIDDLE_PASSIVE,
        "pasj": WordDescription.PASSIVE, # Not sure if this is correct
    }

    PARTS_OF_SPEECH_MAP = {
        "conj": WordDescription.CONJUNCTION,
        "prep": WordDescription.PREPOSITION
    }

    CLITIC_MAP = {
        "proclitic": WordDescription.PROCLITIC,
        "enclitic": WordDescription.ENCLITIC
    }

    cached_cases = None
    cached_dialects = None

    @classmethod
    @transaction.atomic
    def import_file(cls, file_name, return_created_objects=False, start_line_number=None, logger=None, raise_exception_on_match_failure=False, **kwargs):

        if logger:
            logger.debug("Importing file, file=\"%s\"", file_name)

        # Record the start time so that we can measure performance
        start_time = time()

        # If we are returning the objects, then initialize an array to store them. Otherwise, initialize the count.
        if return_created_objects:
            objects = []
        else:
            objects = 0

        # Initialize a couple more things...
        f = None  # The file handle
        line_number = 0  # The line number

        try:

            # Open the file
            f = open(file_name, 'r')

            # This will be the line
            formLine = None

            # Process each line
            for line in f:

                # Note the line number we are importing
                line_number = line_number + 1

                # If we are importing starting from a particular line number, then skip lines until you get to this point
                if start_line_number is not None and line_number < start_line_number:
                    pass # Skip this line

                else:
                    # Stop if this is a comment
                    if cls.COMMENT_RE.match(line):
                        if formLine is not None:
                            if raise_exception_on_match_failure:
                                raise Exception("Line %i: Observed a comment line, but we have a form line" % line_number)
                            
                            if logger:
                                logger.warn("Line %i: Observed a comment line, but we have a form line", line_number)

                            formLine = None
                    
                    # Stop if this is an empty line
                    elif line.strip() == "":
                        if formLine is not None:
                            if raise_exception_on_match_failure:
                                raise Exception("Line %i: Observed an empty line, but we have a form line" % line_number)
                            
                            if logger:
                                logger.warn("Line %i: Observed an empty line, but we have a form line", line_number)

                            formLine = None

                    # These are supposed to be two rows; add the first row as the one with the list of matching forms
                    elif formLine is None:
                        formLine = line

                    elif formLine is not None:

                        # Import the line
                        obj = cls.import_line(formLine, line, line_number, **kwargs)

                        # Reset the form line since we are done with it
                        formLine = None

                        # Create the entries

                        if return_created_objects:
                            if obj is not None:
                                objects.extend(obj)
                        else:
                            objects = objects + len(obj)
        finally:
            if f is not None:
                f.close()

        if logger:
            logger.info("Import complete, duration=%i", time() - start_time)

        return objects

    @classmethod
    def import_line(cls, form, entry, line_number=None, raise_exception_on_match_failure=False):
        """
        Parse an entry in the analysis file.

        Example:
            !άβαις|!άβαις
            ἥβη : youthful prime : fem dat pl (doric)

        Arguments:
        entry -- A line in the greek-analysis file
        line_number -- The line number associated with the entry
        """

        # Keep a list of the created forms
        created_forms = []

        # Break up the forms into a list
        possibleForms = cls.FORMS_RE.findall(form)

        # Clean up the forms
        for i in range(len(possibleForms)):
            possibleForms[i] = cls.clean_up_form(possibleForms[i])

        # Break up the entry if it has multiple forms
        definitions = entry.split("<br>")

        # Handle each definition
        for possibleForm in possibleForms:
            for definition in definitions:
                parsed_entry = cls.MAIN_ANALYSIS_RE.match(definition)
                
                lemma_form = parsed_entry.group(1).strip()
                meaning = parsed_entry.group(2).strip()
                details = parsed_entry.group(3).strip()

                word_description = cls.create_word_description(possibleForm, lemma_form, meaning, details, definition)

                if word_description is not None:
                    created_forms.append(word_description)

                # Parse into a list of attributes
                attrs = cls.PARSE_FIND_ATTRS.findall(details)

                # Update the word description with the data from the attributes
                cls.create_description_attributes(attrs, word_description, line_number)

        # Return what we created
        return created_forms

    @classmethod
    def get_word_form(cls, form):
        """
        Get the WordForm associated with the given form.

        Arguments:
        cls -- The class
        form -- The form of the word
        """

        # Find the form if it already exists
        word_form = WordForm.objects.only("form").filter(
            form=form)[:1]

        if len(word_form) > 0:
            return word_form[0]

        # Make the form
        word_form = WordForm()
        word_form.form = form
        word_form.save()

        return word_form

    @classmethod
    def create_word_description(cls, form, lemma_form, meaning, details, desc):
        # Make the form
        word_form = cls.get_word_form(form)

        # Get the lemma
        lemma = cls.get_lemma(lemma_form)

        # Add the description of the form
        word_description = WordDescription(description=desc)
        word_description.word_form = word_form
        word_description.lemma = lemma
        word_description.meaning = meaning

        return word_description

    @classmethod
    def create_description_attributes(cls, attrs, word_description, raise_on_unused_attributes=False, line_number=None):
        """
        Update the description with attributes from the attrs.

        Arguments:
        cls -- The class
        attrs -- The list of attributes
        word_description -- The word description instance to modify
        raise_on_unused_attributes -- Raise an exception if an attribute is observed that is not recognized
        line_number -- The line number of the description we are populating
        """

        dialects = []
        cases = []

        # Go through the attributes and initialize the instance
        for a in attrs:

            # Handle gender
            if a == "fem":
                word_description.feminine = True
                cls.set_part_of_speech(word_description, WordDescription.NOUN)

            elif a == "masc":
                word_description.masculine = True
                cls.set_part_of_speech(word_description, WordDescription.NOUN)

            elif a == "neut":
                word_description.neuter = True
                cls.set_part_of_speech(word_description, WordDescription.NOUN)

            # Handle number
            elif a in cls.NUMBER_MAP:
                word_description.number = cls.NUMBER_MAP[a]

            # Handle dialects
            elif a in ["attic", "doric", "aeolic", "epic", "ionic", "homeric", "parad_form", "prose"]:
                dialects.append(cls.get_dialect(a))

            # Handle part of speech
            elif a in ["adverb", "adverbial"]:
                cls.set_part_of_speech(
                    word_description, WordDescription.ADVERB)

            # Handle number
            elif a in ["indeclform", "indecl"]:
                word_description.indeclinable = True

            # Handle person
            elif a in cls.PERSON_MAP:
                word_description.person = cls.PERSON_MAP[a]

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
            elif a in cls.TENSE_MAP:
                word_description.tense = cls.TENSE_MAP[a]
                cls.set_part_of_speech(word_description, WordDescription.VERB)

            # Handle moods
            elif a in cls.MOOD_MAP:
                word_description.mood = cls.MOOD_MAP[a]
                cls.set_part_of_speech(word_description, WordDescription.VERB)

            elif a == "inf":
                word_description.infinitive = True
                cls.set_part_of_speech(word_description, WordDescription.VERB)

            elif a == "part":
                word_description.participle = True

            elif a == "expletive":
                word_description.expletive = True

            elif a == "poetic":
                word_description.poetic = True

            elif a in cls.PARTS_OF_SPEECH_MAP:
                cls.set_part_of_speech(
                    word_description, cls.PARTS_OF_SPEECH_MAP[a])

            elif a == "particle":
                word_description.particle = True

            elif a in cls.CLITIC_MAP:
                word_description.clitic = cls.CLITIC_MAP[a]

            elif a == "nu_movable":
                word_description.movable_nu = True

            elif a == "numeral":
                word_description.numeral = True

            elif a == "geog_name":
                word_description.geog_name = True

            elif a in ["a_priv", "exclam", "iota_intens", "contr", "alphabetic"]:
                pass

            elif a in cls.VOICE_MAP:
                word_description.voice = cls.VOICE_MAP[a]
                cls.set_part_of_speech(word_description, WordDescription.VERB)

            # Handle cases
            elif a in cls.CASE_MAP:
                cases.append(cls.get_case(cls.CASE_MAP[a]))
                cls.set_part_of_speech(
                    word_description, WordDescription.NOUN, dont_set_if_already_set=True)

            # Warn in the attribute was not processed
            elif raise_on_unused_attributes:

                if line_number is not None:
                    raise Exception(
                        "Attribute was not expected: attribute=%s, line_number=%i" % (a, line_number))
                else:
                    raise Exception(
                        "Attribute was not expected: attribute=%s" % a)

            else:

                if line_number is not None:
                    logger.warn(
                        "Attribute was not expected: attribute=%s, line_number=%i" % (a, line_number))
                else:
                    logger.warn("Attribute was not expected: attribute=%s" % a)

        # Save the description
        word_description.save()

        # Add the cases
        for case in cases:
            word_description.cases.add(case)

        # Add the dialects
        for dialect in dialects:
            word_description.dialects.add(dialect)

        return word_description

    @classmethod
    def get_lemma(cls, lexical_form):
        """
        Get the lemma associated with the given form.

        Arguments:
        cls -- The class
        lexical_form -- The lexical form of the lemma
        """

        lemma = Lemma.objects.only("lexical_form").filter(
            lexical_form=lexical_form)[:1]

        if len(lemma) > 0:
            return lemma[0]

        else:
            # Make the entry
            lemma = Lemma(language="Greek")
            lemma.lexical_form = lexical_form
            lemma.save()

            return lemma

    @classmethod
    def clean_up_form(cls, form):
        """
        Clean up the form.
        """
        if form.startswith("!"):
            return form[1:].strip()

        return form.strip()


    @classmethod
    def get_case(cls, case, raise_exception_if_not_found=False):
        """
        Get a case associated with the provided string.

        Arguments:
        cls -- The class
        case -- A name of a case.
        """

        if cls.cached_cases is None:
            cls.cached_cases = Case.objects.all()

        for c in cls.cached_cases:

            if c.name == case:
                return c

        # Create the new case
        if raise_exception_if_not_found:
            raise Exception("Case %s was not found" % case)
        else:
            new_case = Case(name=case)
            new_case.save()

            cls.cached_cases = None

        return new_case

    @classmethod
    def get_dialect(cls, dialect, raise_exception_if_not_found=False):
        """
        Get a dialect associated with the provided string.

        Arguments:
        cls -- The class
        dialect -- A name of a dialect.
        """

        if cls.cached_dialects is None:
            cls.cached_dialects = Dialect.objects.all()

        for c in cls.cached_dialects:

            if c.name == dialect:
                return c

        # Create the new dialect
        if raise_exception_if_not_found:
            raise Exception("Dialect %s was not found" % dialect)
        else:
            new_dialect = Dialect(name=dialect)
            new_dialect.save()

            cls.cached_dialects = None

            return new_dialect

    @staticmethod
    def set_part_of_speech(word_description, part_of_speech, raise_if_already_set=True, dont_set_if_already_set=True):
        """
        Set the part of speech.

        Arguments:
        word_description -- The word description instance to modify
        part_of_speech -- The part of speech to set
        raise_if_already_set -- Raise an exception if the part of speech was already set to something else
        dont_set_if_already_set -- If the part of speech was already set, then leave the existing value
        """

        if word_description.part_of_speech is not None and word_description.part_of_speech != part_of_speech and part_of_speech and raise_if_already_set:
            raise Exception("Part of speech was unexpected, is %i but was set to %i" % (
                word_description.part_of_speech, part_of_speech))

        if dont_set_if_already_set and word_description.part_of_speech is not None:
            pass

        else:
            word_description.part_of_speech = part_of_speech
