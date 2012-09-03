from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)
    date_born = models.DateTimeField('date of birth')
    date_died = models.DateTimeField('date of death')
    
    # Indicates that the chapter is not a real author but a category (like "unknown" or "various")
    meta_author = models.BooleanField(default=False)
    
    
class Verse(models.Model):
    verse_number = models.IntegerField()
    verse_indicator = models.CharField(max_length=10)
    
    content = models.CharField(max_length=200)
    
class Chapter(models.Model):
    verses = models.ManyToManyField(Verse)
    chapter_number = models.IntegerField()
    chapter_title = models.CharField(max_length=200)
    chapter_subtitle = models.CharField(max_length=200)
    chapter_indicator = models.CharField(max_length=10)
    
class Work(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    translators = models.ManyToManyField(Author, related_name="translators")
    
    date_written = models.DateTimeField('date written')
    language = models.CharField(max_length=200)
    
    chapters = models.ManyToManyField(Chapter)

    
"""
class Section(models.Model):
    chapters = models.ManyToManyField(Chapter)
    sub_sections = models.ManyToManyField(Section)
"""