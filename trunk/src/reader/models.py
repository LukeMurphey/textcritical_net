from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    date_born = models.DateTimeField('date of birth', blank=True, null=True)
    date_died = models.DateTimeField('date of death', blank=True, null=True)
    description = models.TextField(blank=True)
    
    # Indicates that the chapter is not a real author but a category (like "unknown" or "various")
    meta_author = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name

class WorkType(models.Model):
    title = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.title

class Work(models.Model):
    
    list_display = ('title', 'authors', 'language')
    
    title = models.CharField(max_length=200)
    work_type = models.ForeignKey(WorkType, blank=True, null=True)
    authors = models.ManyToManyField(Author, blank=True)
    translators = models.ManyToManyField(Author, blank=True, related_name="translators")
    descriptor = models.CharField(max_length=30, blank=True)
    copyright = models.CharField(max_length=200, blank=True)
    date_written = models.DateTimeField('date written', blank=True, null=True)
    language = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title
    
class Chapter(models.Model):
    work = models.ForeignKey(Work)
    sequence_number = models.IntegerField()
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)
    descriptor = models.CharField(max_length=10, blank=True)
    original_content = models.TextField(blank=True)
    
    def __unicode__(self):
        if self.title is not None and len(self.title) > 0:
            return self.title
        elif self.descriptor is not None and len(self.descriptor) > 0:
            return self.descriptor
        elif self.sequence_number is not None:
            return str(self.sequence_number)
        else:
            return "Chapter object"
    
class Verse(models.Model):
    chapter = models.ForeignKey(Chapter)
    sequence_number = models.IntegerField()
    indicator = models.CharField(max_length=10)
    
    content = models.TextField()
    original_content = models.TextField()
    
    def __unicode__(self):
        if self.indicator is not None and len(self.indicator) > 0:
            return self.indicator
        else:
            return self.sequence_number 
    
class WorkSource(models.Model):
    source = models.CharField(max_length=200)
    resource = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    work = models.ForeignKey(Work)
    
class Section(models.Model):
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200)
    type = models.CharField(max_length=50, blank=True, null=True)
    level = models.IntegerField()
    chapters = models.ManyToManyField(Chapter)
    super_section = models.ForeignKey('self', blank=True, null=True)
    
    def __unicode__(self):
        if self.title is not None and len(self.title) > 0:
            return self.title
        elif self.type is not None and len(self.type) > 0:
            return self.type + " " + str(self.level)
        else:
            return str(self.level)