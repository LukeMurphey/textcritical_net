'''
Created on Sep 2, 2012

@author: Luke
'''

from reader.language_tools import Greek
from reader.models import Lemma, Case, WordForm, WordDescription, Dialect
from reader.importer.LineImporter import LineImporter
import re
import logging
from time import time
from django.db import transaction

logger = logging.getLogger(__name__)


class DiogenesAnalysesImporter(LineImporter):
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
    PARSE_ANALYSIS_DESCRIPTION_RE = re.compile(
        "[{]?(?P<reference_number>[0-9]+)\s+(?P<second_number>[0-9]+)\s+(?P<forms>[^\t]+)\t(?P<definition>.+)\t(?P<attrs>[^}]*)}(\[(?P<extra>[0-9]+)\])?")

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
        "mp": WordDescription.MIDDLE_PASSIVE
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
    def import_line(cls, entry, line_number=None, raise_exception_on_match_failure=False):
        """
        Parse an entry in the Diogenes greek-analyses.txt file.

        Example: 'ch/nta    {10100899 9 e)ch/nta_,e)k-a)nta/w    come opposite to    imperf ind act 3rd sg (attic epic ionic)}[32695571]

        Arguments:
        entry -- A line in the greek-analysis file
        line_number -- The line number associated with the entry
        """

        # Get the form
        beta_code_string = entry[0:entry.find("\t")]

        # Strip out the exclamation marks which isn't necessary from what I can tell and just makes problems
        beta_code_string = beta_code_string.replace("!", "")

        # Find the lemma entry
        greek_code_string = Greek.beta_code_to_unicode(beta_code_string)

        # Cut out the stray apostraphe's
        greek_code_string = greek_code_string.replace("'", "")

        # Make the form
        word_form = WordForm()
        word_form.form = greek_code_string
        word_form.save()

        # Make the descriptions
        form_number = 0

        for desc in cls.PARSE_ANALYSIS_DESCRIPTIONS_RE.findall(entry):
            form_number = form_number + 1
            DiogenesAnalysesImporter.import_analysis_entry(
                desc, word_form, line_number, form_number, raise_exception_on_match_failure)

        # Log the line
        if line_number is not None and (line_number % 1000) == 0:
            logger.info("Importation progress, line_number=%i", line_number)

        return word_form

    @classmethod
    def get_lemma(cls, reference_number):
        """
        Get the lemma associated with the given reference number.

        Arguments:
        cls -- The class
        reference_number -- The reference number associated with the lemma
        """

        lemma = Lemma.objects.only("id").filter(
            reference_number=reference_number)[:1]

        if len(lemma) > 0:
            return lemma[0]

    @classmethod
    def import_analysis_entry(cls, desc, word_form, line_number=None, form_number=None, raise_exception_on_match_failure=False):
        """
        Import an entry from the Diogenes lemmata file.

        Arguments:
        cls -- The class
        desc -- A string with the part of the line that describes the given form (e.g. "{537850 9 a(/bra_,a(/bra    favourite slave    fem nom/voc/acc dual}")
        word_form -- The WordForm instance associated with the description
        line_number -- The line number that this entry is found on
        form_number -- The number of the form on this line (since each line can have several forms)
        raise_exception_on_match_failure -- Indicates if an exception should be raised if the line could not be matched to the regular expression
        """

        # Parse the description
        r = cls.PARSE_ANALYSIS_DESCRIPTION_RE.search(desc)

        # Stop if the regex did not match
        if r is None:

            if raise_exception_on_match_failure:
                raise Exception("Analysis entry does not match the regex, form=%s, line_number=%r, form_number=%r" % (
                    word_form.form, line_number, form_number))

            logger.warning("Analysis entry does not match the regex, form=%s, line_number=%r, form_number=%r" % (
                word_form.form, line_number, form_number))
            return

        d = r.groupdict()

        # Find the entry associated by the reference number
        reference_number = d['reference_number']
        lemma = cls.get_lemma(reference_number)

        # Stop if we couldn't find a matching lemma
        if lemma is None:
            logger.warning("Unable to find the lemma for an analysis entry, form=%s, reference_number=%r, line_number=%r, form_number=%r" % (
                word_form.form, reference_number, line_number, form_number))
        else:

            # Add the description of the form
            word_description = WordDescription(description=desc)
            word_description.word_form = word_form
            word_description.lemma = lemma
            word_description.meaning = d['definition']

            # Parse into a list of attributes
            attrs = cls.PARSE_FIND_ATTRS.findall(d['attrs'])

            # Update the word description with the data from the attributes
            return cls.create_description_attributes(attrs, word_description, line_number)

    @classmethod
    def get_case(cls, case):
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
        new_case = Case(name=case)
        new_case.save()

        cls.cached_cases = None

        return new_case

    @classmethod
    def get_dialect(cls, dialect):
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
                cases.append(cls.get_case(a))
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
                    logger.warning(
                        "Attribute was not expected: attribute=%s, line_number=%i" % (a, line_number))
                else:
                    logger.warning("Attribute was not expected: attribute=%s" % a)

        # Save the description
        word_description.save()

        # Add the cases
        for case in cases:
            word_description.cases.add(case)

        # Add the dialects
        for dialect in dialects:
            word_description.dialects.add(dialect)

        return word_description


class DiogenesLemmataImporter():
    """
    The Diogenes Lemmata importer imports the lemmata file (greek-lemmata.txt) from the Diogenes project.
    """

    @staticmethod
    @transaction.atomic
    def parse_lemma(entry, line_number=None):
        """
        Parse an entry in the Diogenes greek-lemmata.txt file.

        Example: 'ch/nta    {10100899 9 e)ch/nta_,e)k-a)nta/w    come opposite to    imperf ind act 3rd sg (attic epic ionic)}[32695571]

        Arguments:
        entry -- A line in the greek-lemmata file
        line_number -- The line number associated with the entry
        """

        split_entry = entry.split("\t")

        # Convert the beta-code to Greek
        lexical_form = Greek.beta_code_str_to_unicode(split_entry[0])

        # Cut out unnecessary apostrophe's
        lexical_form = lexical_form.replace("'", "")

        # Get the reference number
        reference_number = int(split_entry[1])

        # Make the entry
        lemma = Lemma(language="Greek")
        lemma.lexical_form = lexical_form
        lemma.reference_number = reference_number
        lemma.save()

        return lemma

    @staticmethod
    def import_file(file_name, return_created_objects=False, start_line_number=None):

        logger.debug("Importing file, file=\"%s\"", file_name)

        # Record the start time so that we can measure performance
        start_time = time()

        # If we are returning the objects, then initialize an array to store them. Otherwise, intialize the count.
        if return_created_objects:
            lemmas = []
        else:
            lemmas = 0

        # Initialize a couple more things...
        f = None  # The file handle
        line_number = 0  # The line number

        try:

            # Open the file
            f = open(file_name, 'r')

            # Process each line
            for line in f:

                # Note the line number we are importing
                line_number = line_number + 1

                # If we are importing starting from a particular line number, then skip lines until you get to this point
                if start_line_number is not None and line_number < start_line_number:
                    pass  # Skip this line

                else:
                    # Import the line
                    lemma = DiogenesLemmataImporter.parse_lemma(
                        line, line_number)

                    if return_created_objects:
                        lemmas.append(lemma)
                    else:
                        lemmas = lemmas + 1
        finally:
            if f is not None:
                f.close()

        logger.info("Import complete, duration=%i", time() - start_time)

        return lemmas
