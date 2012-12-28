from django.db import models
from django.template.defaultfilters import slugify
import re
import unicodedata
from reader import language_tools

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
        
    def save(self, *args, **kwargs):
        
        if not self.id and not self.title_slug:
            
            # Newly created object, so set slug
            self.title_slug = self.get_slug_title()

        super(Division, self).save(*args, **kwargs)
        
    def get_division_description(self, use_titles=False):
        
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
            is_number = re.match("[0-9]+", title)
            
            # Put a period between the numbers
            if s is not None and prior_was_number and is_number:
                s = "." + s
            else:
                s = " " + s
                
            prior_was_number = is_number
                
            # Add the title
            if s is None:
                s = title
            else:
                s = title + s
            
            # Get the next division
            next_division = next_division.parent_division
            
        return s.strip()
    
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
        
        # Normalize the content so that we can do searches by normalizing to 
        self.content = language_tools.normalize_unicode( self.content )
    
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
    