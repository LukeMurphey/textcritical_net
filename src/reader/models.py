# -*- coding: utf-8 -*-
"""
The following models are currently included:

+-----------------+-----------------------------------------------------------+
| Model           | Description                                               |
+-----------------+-----------------------------------------------------------+
| Author          | Identifies the author of a work                           |
|-----------------|-----------------------------------------------------------|
| WorkType        | The type of a work (poem, etc.)                           |
|-----------------|-----------------------------------------------------------|
| Work            | A description of a work                                   |
|-----------------|-----------------------------------------------------------|
| RelatedWork     | The relation between two works                            |
|-----------------|-----------------------------------------------------------|
| WorkAlias       | An alias to refer to a work (in case it changes names)    |
|-----------------|-----------------------------------------------------------|
| Division        | A division of a work (chapter, etc.)                      |
|-----------------|-----------------------------------------------------------|
| Verse           | A verse within the work                                   |
|-----------------|-----------------------------------------------------------|
| WorkSource      | A definition of where a work came from                    |
|-----------------|-----------------------------------------------------------|
| Lemma           | A root word                                               |
|-----------------|-----------------------------------------------------------|
| Case            | A word's case                                             |
|-----------------|-----------------------------------------------------------|
| Dialect         | A dialect of a word                                       |
|-----------------|-----------------------------------------------------------|
| WordForm        | A form of a particular word (declined version)            |
|-----------------|-----------------------------------------------------------|
| WordDescription | The meaning of a particular form of a word                |
|-----------------|-----------------------------------------------------------|
| WikiArticle     | The information necessary to look up a topic on Wikipedia |
|-----------------|-----------------------------------------------------------|
"""

from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

import logging
import re
from reader import language_tools

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Author(models.Model):
    """
    Identifies the author of a work.
    """
    
    name        = models.CharField(max_length=200)
    name_slug   = models.SlugField()
    first_name  = models.CharField(max_length=200, blank=True)
    last_name   = models.CharField(max_length=200, blank=True)
    date_born   = models.DateTimeField('date of birth', blank=True, null=True)
    date_died   = models.DateTimeField('date of death', blank=True, null=True)
    description = models.TextField(blank=True)
    
    # Indicates that the chapter is not a real author but a category (like "unknown" or "various")
    meta_author = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        
        if not self.id and not self.name_slug:
            # Newly created object, so set slug
            self.name_slug = slugify(self.name)

        super(Author, self).save(*args, **kwargs)

class WorkType(models.Model):
    """
    Identifies the type of work. Such as a book, poem, etc.
    """
    
    title = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.title

class Work(models.Model):
    """
    Represents a work (normally a book).
    """
    
    list_display = ('title', 'authors', 'language')
    
    title        = models.CharField(max_length=200)
    title_slug   = models.SlugField(unique=True)
    
    work_type    = models.ForeignKey(WorkType, blank=True, null=True)
    authors      = models.ManyToManyField(Author, blank=True)
    editors      = models.ManyToManyField(Author, blank=True, related_name="editors")
    descriptor   = models.CharField(max_length=30, blank=True)
    copyright    = models.CharField(max_length=200, blank=True)
    date_written = models.DateTimeField('date written', blank=True, null=True)
    language     = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        
        if not self.id and not self.title_slug:
            # Newly created object, so set slug
            self.title_slug = slugify(self.title)

        super(Work, self).save(*args, **kwargs)
        

class RelatedWork(models.Model):
    """
    Represents a relationship between two works.
    """
    
    work           = models.ForeignKey(Work, related_name="work")
    related_work   = models.ForeignKey(Work, related_name="related_work")
    related_levels = models.IntegerField(null=True)
    
    class Meta:
        unique_together = ("work", "related_work")
    
    @staticmethod
    def are_divisions_identical( first_work, second_work ):
        """
        Determine if the divisions in the given works appear to be identical.
        """
        
        # Get a list of the divisions
        divisions_first_work = Division.objects.filter( work = first_work ).order_by( "sequence_number" )
        divisions_second_work = Division.objects.filter( work = second_work ).order_by( "sequence_number" )
        
        # Make sure the divisions are consistent
        if divisions_first_work.count() != divisions_second_work.count():
            logger.info("Division counts are different, these works are not identical, first_work=%s, second_work=%s",  first_work.title_slug, second_work.title_slug )
            return False
        
        # Compare the divisions
        for i in range(0, divisions_first_work.count() ):
            
            # Compare the divisions
            if divisions_first_work[i].descriptor != divisions_second_work[i].descriptor:
                logger.info("Division counts are different, these works are not identical, first_work=%s, division_first_work=%s, second_work=%s, division_second_work=%s", divisions_first_work[i].work.title_slug, divisions_first_work[i].title_slug, divisions_second_work[i].work.title_slug, divisions_second_work[i].title_slug )
                return False
            
        return True
    
    @classmethod
    def are_works_equivalent( cls, first_work, second_work, ignore_editors=False, ignore_divisions=False, consider_a_match_if_divisions_or_editors_match=True ):
        """
        Determine if these works appear to be identical.
        """
        
        if first_work.title != second_work.title:
            return False
        
        # Compare the authors
        first_work_authors = first_work.authors.all().order_by("name")
        second_work_authors = second_work.authors.all().order_by("name")
        
        if first_work_authors.count() != second_work_authors.count():
            logger.info("Works are not identical, author counts are different, first_work=%s, second_work=%s" % ( first_work.title_slug, second_work.title_slug) )
            return False
        
        for i in range(0, first_work_authors.count() ):
            if first_work_authors[i].name != second_work_authors[i].name:
                logger.info("Works are not identical, author is different, first_work=%s, second_work=%s, first_work_author=%s, second_work_author=%s" % ( first_work.title_slug, second_work.title_slug, first_work_authors[i].name, second_work_authors[i].name) )
                return False
        
        # Compare the editors
        editors_match = None
        
        if not ignore_editors or consider_a_match_if_divisions_or_editors_match:
            first_work_editors = first_work.editors.all().order_by("name")
            second_work_editors = second_work.editors.all().order_by("name")
            
            # Match up the count of editors
            if first_work_editors.count() != second_work_editors.count():
                editors_match = False
            
            # If the count is the same, then check the values
            if editors_match is None:
                for i in range(0, first_work_editors.count() ):
                    if first_work_editors[i].name != second_work_editors[i].name:
                        logger.info("Works are not identical, editor is different, first_work=%s, second_work=%s, first_work_editor=%s, second_work_editor=%s" % ( first_work.title_slug, second_work.title_slug, first_work_editors[i].name, second_work_editors[i].name) )
                        editors_match = False
                
                editors_match = True
        
        # Compare the divisions
        divisions_match = None
        
        if not ignore_divisions or consider_a_match_if_divisions_or_editors_match:
            divisions_match = cls.are_divisions_identical( first_work, second_work )
        
        # If we are considering this a match if the editors or divisions match, then evaluate accordingly
        if consider_a_match_if_divisions_or_editors_match:
            
            if editors_match or divisions_match:
                logger.info("Works are identical since editors or divisions match, first_work=%s, second_work=%s", first_work.title_slug, second_work.title_slug )
                return True
            else:
                logger.info("Works are not identical, since the neither the divisions nor the editors matched, first_work=%s, second_work=%s", first_work.title_slug, second_work.title_slug )
                return False   
             
        # Stop if the divisions don't match but should
        elif not ignore_divisions and not divisions_match:
            return False
        
        # Stop if the editors don't match but should
        elif not ignore_editors and not editors_match:
            return False
        
        # If we failed to reject the equivalency of the work, then treat them as equivalent
        return True
    
    @staticmethod
    def make_related_work(first_work, second_work):
        
        entries_made = 0
        
        # Make the reference for the first work
        if RelatedWork.objects.filter(work=first_work, related_work=second_work).count() == 0:
            related_work = RelatedWork(work=first_work, related_work=second_work)
            related_work.save()
            entries_made = entries_made + 1
                    
        # Make the reference backwards
        if RelatedWork.objects.filter(work=second_work, related_work=first_work).count() == 0:
            related_work2 = RelatedWork(work=second_work, related_work=first_work)
            related_work2.save()
            entries_made = entries_made + 1
            
        return entries_made
    
    @classmethod
    def autodiscover( cls, ignore_editors=False, ignore_divisions=False, consider_a_match_if_divisions_or_editors_match=True ):
        """
        Automatically discover related works and make references to them.
        """
        
        for first_work in Work.objects.all():
            cls.find_related_for_work(first_work, ignore_editors, ignore_divisions, consider_a_match_if_divisions_or_editors_match)
            
    @classmethod
    def find_related_for_work( cls, first_work, ignore_editors=False, ignore_divisions=False, consider_a_match_if_divisions_or_editors_match=True, test=False ):
        """
        Automatically discover any other related works and make a reference to the provided work.
        """

        related_works = []

        for second_work in Work.objects.all():

            if second_work.id != first_work.id and cls.are_works_equivalent(first_work, second_work, ignore_editors, ignore_divisions, consider_a_match_if_divisions_or_editors_match):

                if not test:
                    # Make the related work instances
                    entries_made = RelatedWork.make_related_work(first_work, second_work)

                    if entries_made > 0:
                        logger.info("Made a reference between two works, first_work=%s, second_work=%s" % ( first_work.title_slug, second_work.title_slug) )

                # Keep a record of the related work
                related_works.append(second_work)

        return related_works

class WorkAlias(models.Model):
    """
    Represents an alias to a work.
    """
    
    title_slug = models.SlugField(unique=True)
    work       = models.ForeignKey(Work, blank=False, null=False)
    
    @staticmethod
    def populate_from_existing():
        works = Work.objects.all()
        
        items_created = 0
        
        for work in works:
            
            if WorkAlias.populate_alias_from_work(work) is not None:
                items_created = items_created + 1
    
        return items_created
    
    @staticmethod
    def populate_alias_from_work( work ):
        
        # If the title_slug is empty, then just ignore this for now
        if work.title_slug is None or len(work.title_slug) == 0:
            return None
        
        # Determine if the entry already exists for this work
        if WorkAlias.objects.filter(title_slug=work.title_slug, work=work).count() >= 1:
            return None
        
        # Determine if the entry exists for another work
        if WorkAlias.objects.filter(title_slug=work.title_slug).exclude(work=work).count() >= 1:
            raise Exception("Alias already exists for another work")
                
        # Otherwise, make the new entry
        work_alias = WorkAlias( title_slug=work.title_slug, work=work )
        work_alias.save()
        
        return work_alias
    
class Division(models.Model):
    """
    Represents a collection of verses for the purpose of providing a structure
    of documents.
    """
    
    work             = models.ForeignKey(Work)
    sequence_number  = models.IntegerField()
    
    title            = models.CharField(max_length=200, blank=True, null=True)
    title_slug       = models.SlugField()
    original_title   = models.CharField(max_length=200, blank=True, null=True)
    subtitle         = models.CharField(max_length=200, blank=True)
    descriptor       = models.CharField(max_length=10, db_index=True)
    
    type             = models.CharField(max_length=50, blank=True, null=True)
    level            = models.IntegerField()
    
    original_content = models.TextField(blank=True)
    
    parent_division  = models.ForeignKey('self', blank=True, null=True)
    readable_unit    = models.BooleanField(default=False, db_index=True)
    
    def __unicode__(self):
        if self.title is not None and len(self.title) > 0:
            return self.title
        elif self.descriptor is not None and self.type is not None:
            return str(self.type) + " " + str(self.descriptor)
        elif self.descriptor is not None:
            return str(self.descriptor)
        elif self.sequence_number is not None:
            return str(self.sequence_number)
        else:
            return "Division object"
    
    def get_slug_title(self):
        
        if self.original_title is not None:
            return slugify( re.sub("[)'(+*=|/\\\\]", "", self.original_title) )
        elif self.descriptor is not None:
            return slugify( self.descriptor )
        else:
            return slugify( self.sequence_number )
        
    def update_title_slug(self):
        self.title_slug = self.get_slug_title()
        
    def save(self, *args, **kwargs):
        
        if not self.id and not self.title_slug:
            
            # Newly created object, so set slug
            self.update_title_slug()

        super(Division, self).save(*args, **kwargs)
        
    def get_division_description(self, use_titles=False, verse=None, section_divider=" "):
        
        s = ""
        prior_was_number = False
        
        next_division = self
        
        # Keep recursing upwards until we hit the top
        while next_division is not None:
            
            # Get the title that we are going to use
            if use_titles:
                title = str(next_division)
            else:
                title = next_division.descriptor
            
            # Determine if this is a number
            is_number = re.match("^[0-9]+ ?$", title)
            
            # Put a period between the numbers
            if s is not None and prior_was_number and is_number:
                s = "." + s
            else:
                s = section_divider + s
                
            prior_was_number = is_number
                
            # Add the title
            if s is None:
                s = title
            else:
                s = title + s
            
            # Get the next division
            next_division = next_division.parent_division
            
        # Make sure we don't have any trailing spaces
        s = s.strip()
            
        # Add the verse information and use the correct separator
        if verse:
            if '.' in s:
                s = s + "." + str(verse)
            else:
                s = s + ":" + str(verse)
            
            s = s.strip()
        
        # Return the result
        return s
    
    def get_division_description_titles(self):
        return self.get_division_description(True)
        
    def get_division_indicators(self, use_titles=False):
        """
        Make a list of the divisions.
        """
        
        descriptors = []
        
        next_division = self
        
        # Keep recursing upwards until we hit the top
        while next_division is not None:
            
            # Insert the descriptor at position zero, since the highest level will be at the lowest ID
            if use_titles:
                descriptors.insert(0, str(next_division) )
            else:
                descriptors.insert(0, next_division.descriptor)
            
            # Get the next division
            next_division = next_division.parent_division
            
        return descriptors
    
    def get_division_titles(self):
        return self.get_division_indicators(use_titles=True)
        
    
class Verse(models.Model):
    """
    Represents a verse within a chapter of a work.
    """
    
    division          = models.ForeignKey(Division)
    sequence_number   = models.IntegerField()
    indicator         = models.CharField(max_length=10)
    
    content           = models.TextField()
    original_content  = models.TextField()
    
    def __unicode__(self):
        if self.indicator is not None and len( self.indicator ) > 0:
            return self.indicator
        else:
            return unicode(self.sequence_number)
        
    def save(self, *args, **kwargs):
        
        # Normalize the content so that we can do searches by normalizing to the same form of Unicode
        if isinstance( self.content, str):
            self.content = language_tools.normalize_unicode( unicode(self.content, "UTF-8", 'strict') )
        else:
            self.content = language_tools.normalize_unicode( self.content )
        
        super(Verse, self).save(*args, **kwargs)
    
class WorkSource(models.Model):
    """
    Identifies were a work came from (the file, website, etc.).
    """
    
    source      = models.CharField(max_length=200)
    resource    = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    work        = models.ForeignKey(Work)
    
class Lemma(models.Model):
    """
    Represents a root word.
    """
    
    lexical_form = models.CharField(max_length=200, db_index=True)
    basic_lexical_form = models.CharField(max_length=200, db_index=True)
    language = models.CharField(max_length=40)
    reference_number = models.IntegerField(db_index=True)
    
    def __unicode__(self):
        return unicode(self.lexical_form)
    
    def save(self, *args, **kwargs):
        
        # Normalize the form to NFKC so that we can do queries reliably
        self.lexical_form = language_tools.normalize_unicode( self.lexical_form )
        
        # Save the basic form
        self.basic_lexical_form = language_tools.strip_accents( self.lexical_form )

        super(Lemma, self).save(*args, **kwargs)
    
class Case(models.Model):
    """
    Represents various cases.
    """
    
    # Case
    VOCATIVE   = "vocative"
    ACCUSATIVE = "accusative"
    NOMINATIVE = "nominative"
    DATIVE     = "dative"
    GENITIVE   = "genitive"
    
    CASES = (VOCATIVE, ACCUSATIVE, NOMINATIVE, DATIVE, GENITIVE)
    
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return unicode(self.name)
    
class Dialect(models.Model):
    """
    Represents various dialects.
    """
    
    name = models.CharField(max_length=60)
    
    def __unicode__(self):
        return unicode(self.name)
    
class WordForm(models.Model):
    """
    Represents a particular form of a word (taking into account what a declension would look like).
    """
    
    form = models.CharField(max_length=200, db_index=True)
    basic_form = models.CharField(max_length=200, db_index=True)
    
    def __unicode__(self):
        return unicode(self.form)
    
    def save(self, *args, **kwargs):
        
        # Normalize the form to NFKC so that we can do queries reliably
        self.form = language_tools.normalize_unicode(self.form)
        
        # Save the basic form
        self.basic_form = language_tools.strip_accents( self.form )

        super(WordForm, self).save(*args, **kwargs)
    
class WordDescription(models.Model):
    """
    Describes one potential meaning for a given word form.
    """
    
    # Number
    SINGULAR = 0
    DUAL     = 1
    PLURAL   = 2
    
    NUMBER = (
        ('', ''),
        (SINGULAR, 'Singular'),
        (DUAL,     'Dual'),
        (PLURAL,   'Plural')
    )
    
    # Parts of speech
    NOUN         = 0
    VERB         = 1
    ADVERB       = 2
    PRONOUN      = 3
    ADJECTIVE    = 4
    PREPOSITION  = 5
    CONJUNCTION  = 6
    INTERJECTION = 7
    
    PARTS_OF_SPEECH = (
        ('', ''),
        (NOUN, 'Noun'),
        (VERB, 'Verb'),
        (ADVERB, 'Adverb'),
        (PRONOUN, 'Pronoun'),
        (ADJECTIVE, 'Adjective'),
        (PREPOSITION, 'Preposition'),
        (CONJUNCTION, 'Conjunction'),
        (INTERJECTION, 'Interjection')
    )
    
    # Person
    FIRST =  1
    SECOND = 2
    THIRD =  3
    
    PERSON = (
        ('', ''),
        (FIRST,  'First'),
        (SECOND, 'Second'),
        (THIRD,  'Third')
    )
    
    # Voice
    ACTIVE         = 0
    MIDDLE         = 1
    PASSIVE        = 2
    MIDDLE_PASSIVE = 3
    
    VOICE = (
        ('', ''),
        (ACTIVE, 'Active'),
        (MIDDLE, 'Middle'),
        (PASSIVE,'Passive'),
        (MIDDLE_PASSIVE,'Middle/Passive')
    )
    
    # Clitic
    PROCLITIC  = 0
    ENCLITIC   = 1
    MESOCLITIC = 2
    ENDOCLITIC = 3
    
    CLITIC = (
        ('', ''),
        (PROCLITIC, 'Proclitic'),
        (ENCLITIC,  'Enclitic'),
        (MESOCLITIC,'Mesoclitic'),
        (ENDOCLITIC,'Endoclitic')
    )
    
    # Superlatives and comparatives
    REGULAR   = 0
    IRREGULAR = 1
    
    REGULARITY = (
        ('', ''),
        (REGULAR, 'Regular'),
        (IRREGULAR, 'Irregular'),
    )
    
    # Attributes associated with nouns
    masculine      = models.NullBooleanField(default=False)
    feminine       = models.NullBooleanField(default=False)
    neuter         = models.NullBooleanField(default=False)
    
    cases          = models.ManyToManyField(Case)
    geog_name      = models.NullBooleanField(default=None, null=True)
    numeral        = models.NullBooleanField(default=None, null=True)
    
    # Attributes associated with verbs
    adverb         = models.NullBooleanField(default=None, null=True)
    infinitive     = models.NullBooleanField(default=None, null=True)
    participle     = models.NullBooleanField(default=None, null=True)
    voice          = models.IntegerField(choices=VOICE, default=None, null=True)
    mood           = models.CharField(max_length=100, default=None, null=True)
    tense          = models.CharField(max_length=100, default=None, null=True)
    
    # Attributes associated with verbs and nouns 
    person         = models.IntegerField(choices=PERSON, default=None, null=True)
    number         = models.IntegerField(choices=NUMBER, default=None, null=True)
    dialects       = models.ManyToManyField(Dialect)
    part_of_speech = models.IntegerField(choices=PARTS_OF_SPEECH, default=None, null=True)
    indeclinable   = models.NullBooleanField(default=None, null=True)
    particle       = models.NullBooleanField(default=None, null=True)
    
    superlative    = models.IntegerField(choices=REGULARITY, default=None, null=True)
    comparative    = models.IntegerField(choices=REGULARITY, default=None, null=True)
    expletive      = models.NullBooleanField(default=None, null=True)
    poetic         = models.NullBooleanField(default=None, null=True)
    clitic         = models.IntegerField(choices=CLITIC, default=None, null=True)
    
    movable_nu     = models.NullBooleanField(default=None, null=True)
    
    lemma          = models.ForeignKey(Lemma)
    word_form      = models.ForeignKey(WordForm)
    description    = models.CharField( max_length=50, default="", null=True)
    
    meaning        = models.CharField( max_length=200, default="", null=True)
    
    # This class replaces some well-known terms with shorter versions
    SHORTENERS = {
                  'Feminine'  : 'fem',
                  'Masculine' : 'masc',
                  'Neuter'    : 'nuet',
                  
                  'Singular' : 'sg',
                  'Plural'   : 'pl',
                  
                  'First'  : '1st',
                  'Second' : '2nd',
                  'Third'  : '3rd',
                  
                  'present'           : 'pres',
                  'imperfect'         : 'impf',
                  'aorist'            : 'aor',
                  'future'            : 'fut',
                  'perfect'           : 'perf',
                  'future perfect'    : 'futperf',
                  'pluperfect'        : 'plup',
                  
                  'Active'         : 'act',
                  'Passive'        : 'pass',
                  'Middle'         : 'mid',
                  'Middle/Passive' : 'mid-pass',
                  
                  'indicative'    : 'ind',
                  'imperative'    : 'imperat',
                  'subjunctive'   : 'subj',
                  'optative'      : 'opt',
                  'interrogative' : 'interrog',
                  
                  'infinitive' : 'inf',
                  'participle' : 'part'
                  
                  }
    
    def shorten(self, value):
        return WordDescription.SHORTENERS.get(value, value)
    
    def append_if_not_none(self, a, entry):
        if entry is not None:
            a.append( self.shorten(entry) )
            
    def append_if_true(self, a, value, str_value):
        
        if value:
            a.append( self.shorten(str_value) )
    
    def __unicode__(self):
        
        a = []
        
        self.append_if_not_none(a, self.tense)
        self.append_if_true(a, self.participle, "participle")
        self.append_if_true(a, self.infinitive, "infinitive")
        self.append_if_not_none(a, self.get_voice_display() )

        # Add the genders
        genders = []
        
        if self.masculine:
            genders.append("masc")
            
        if self.feminine:
            genders.append("fem")
            
        if self.neuter:
            genders.append("nuet")
            
        self.append_if_not_none(a, "/".join(genders) )
        
        # Add the cases
        cases = []
        
        for c in self.cases.all():
            cases.append(c.name)
            
        self.append_if_not_none(a, "/".join(cases) )
        
        self.append_if_not_none(a, self.mood)
        
        self.append_if_not_none(a, self.get_person_display() )
        self.append_if_not_none(a, self.get_number_display() )
        
        self.append_if_true(a, self.part_of_speech == WordDescription.ADVERB, "adverbial")
        self.append_if_true(a, self.indeclinable, "indeclinable")
            
        if self.clitic:
            pass
            
        if self.comparative:
            pass
        
        return unicode(" ".join(a).strip().lower())

class WikiArticle(models.Model):
    """
    Links Wiki articles to search terms.
    """
    
    search = models.CharField(max_length=200, db_index=True, unique=True)
    article = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.search)
    
    @classmethod
    def get_wiki_article(cls, terms=None):
        
        # Make sure the terms provided are an array
        if not isinstance(terms, list) and isinstance(terms, basestring):
            
            try:
                logger.info("Looking for %r", terms)
                wiki = WikiArticle.objects.get(search=terms)
                return wiki.article
            except ObjectDoesNotExist:
                return None
        
        # Try to find each term, return the first one
        for term in terms:
            wiki = cls.get_wiki_article(term)
            
            if wiki is not None:
                return wiki

@receiver(post_save, sender=Work)
def work_alias_create(sender, instance, signal, created, **kwargs):
    WorkAlias.populate_alias_from_work(instance)