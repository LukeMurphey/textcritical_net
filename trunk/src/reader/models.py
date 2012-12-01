from django.db import models
from django.template.defaultfilters import slugify
import re

class Author(models.Model):
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
    title = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.title

class Work(models.Model):
    
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
    descriptor       = models.CharField(max_length=10)
    
    type             = models.CharField(max_length=50, blank=True, null=True)
    level            = models.IntegerField()
    
    original_content = models.TextField(blank=True)
    
    parent_division  = models.ForeignKey('self', blank=True, null=True)
    readable_unit    = models.BooleanField(default=False)
    
    def __unicode__(self):
        if self.title is not None and len(self.title) > 0:
            return self.title
        elif self.descriptor is not None and len(str(self.descriptor)) > 0:
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
    
class WorkSource(models.Model):
    source      = models.CharField(max_length=200)
    resource    = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    work        = models.ForeignKey(Work)