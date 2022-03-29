from reader.language_tools import Greek
from reader.models import Lemma, Case, WordForm, WordDescription, Dialect
from reader.importer.greek_analyses_parser import GreekAnalysesParser
from reader import utils
import re
import logging
from time import time
from django.db import transaction

default_logger = logging.getLogger(__name__)

class RosenAnalysesImporter(GreekAnalysesParser):
    """
    Importer for the analyses of words in the Greek language from the file made by Jacob Rosen.

    The source for this was from:
      * http://www.mobileread.mobi/forums/showthread.php?t=256360
      * https://latin-dict.github.io/dictionaries/morphology-grc.html

    The analyses files can now be obtained from https://github.com/LukeMurphey/ancient-greek-analyses
    """

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

    def __init__(self, raise_exception_on_match_failure=False, logger=None):
        self.logger = logger
        self.raise_exception_on_match_failure = raise_exception_on_match_failure

    @classmethod
    def import_file(cls, file_name, return_created_objects=False, start_line_number=None, logger=None, raise_exception_on_match_failure=False, **kwargs):

        if logger:
            logger.debug("Importing file, file=\"%s\"", file_name)

        # Record the start time so that we can measure performance
        start_time = time()

        # Initialize the file handle
        f = None

        # Initialize the objects to return
        objects = None

        try:
            # Open the file
            f = open(file_name, 'r')

            # Start the import process
            importer = RosenAnalysesImporter(raise_exception_on_match_failure, logger)
            objects = importer.parse_file(f, return_created_objects, start_line_number, logger, raise_exception_on_match_failure)

        finally:
            if f is not None:
                f.close()

        if logger:
            logger.info("Import complete, duration=%i", time() - start_time)

        return objects

    @classmethod
    def get_word_form(cls, form):
        """
        Get the WordForm associated with the given form.

        Arguments:
        cls -- The class
        form -- The form of the word
        """

        # Find the form if it already exists
        word_form = utils.get_word_form(form)

        if word_form is not None:
            return word_form

        # Make the form
        word_form = WordForm()
        word_form.form = form
        word_form.save()

        return word_form

    @transaction.atomic
    def process_word_description(self, form, lexical_form, meaning, details, attrs, description):
        # Make the form
        word_form = self.get_word_form(form)

        # Get the lemma
        lemma = self.get_or_make_lemma(lexical_form)

        # Add the description of the form
        word_description = WordDescription(description=description)
        word_description.word_form = word_form
        word_description.lemma = lemma
        word_description.meaning = meaning

        self.create_description_attributes(attrs, word_description)

        return word_description

    @classmethod
    def create_description_attributes(cls, attrs, word_description, raise_on_unused_attributes=False, line_number=None, logger=None):
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
    def get_or_make_lemma(cls, lexical_form):
        """
        Get the lemma associated with the given form.

        Arguments:
        cls -- The class
        lexical_form -- The lexical form of the lemma
        """

        lemma = utils.get_lemma(lexical_form)

        if lemma is not None:
            return lemma

        else:
            # Make the entry
            lemma = Lemma(language="Greek")
            lemma.lexical_form = lexical_form
            lemma.save()

            return lemma

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
