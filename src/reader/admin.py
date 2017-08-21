import os

from reader.models import Author, Work, WorkType, Division, Verse, Lemma, WordForm, WordDescription, WikiArticle, RelatedWork
from django.contrib import admin
from reader.contentsearch import WorkIndexer
from django.conf import settings
from reader.models import Work
from reader.ebook import MobiConvert
from reader.ebook import ePubExport

class AuthorAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'name_slug', 'date_born', 'date_died', 'meta_author'),
        }),
    )

admin.site.register(Author, AuthorAdmin)

class VerseInline(admin.StackedInline):
    model = Verse
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ( ('indicator', 'sequence_number'), 'content', 'original_content'),
        }),
    )

class DivisionModel(admin.ModelAdmin):
    
    list_display = ('work', 'descriptor', 'sequence_number', 'title', 'type', 'level', 'readable_unit', 'parent_division')
    list_filter = ('work', 'level', 'type',)
    search_fields = ('title','original_content',)
    
    inlines = [
        VerseInline,
    ]
    
class DivisionInline(admin.StackedInline):
    model = Division
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ( ('descriptor', 'sequence_number'), ('title', 'subtitle', 'title_slug'), 'original_content'),
        }),
    )

# A command to make search indexes
def make_search_indexes(modeladmin, request, queryset):
    for work in queryset:
        WorkIndexer.delete_work_index(work)
        WorkIndexer.index_work(work)

make_search_indexes.short_description = "Make search indexes"

# A command to make ebooks
def make_ebooks(modeladmin, request, queryset):
    for work in queryset:

        # Make the directory if necessary
        if not os.path.exists(settings.GENERATED_FILES_DIR):
            os.makedirs(settings.GENERATED_FILES_DIR)

        # Step 1: create the epub file

        epub_file = work.title_slug + ".epub"
        epub_file_full_path = os.path.join(settings.GENERATED_FILES_DIR, epub_file)
                
        # Delete the existing epub file if necessary
        if os.path.exists(epub_file_full_path):
            os.remove(epub_file_full_path)
        
        ePubExport.exportWork(work, epub_file_full_path)

        # Step 2: make the mobi file
        mobi_file = work.title_slug + ".mobi"
        mobi_file_full_path = os.path.join(settings.GENERATED_FILES_DIR, mobi_file)

        MobiConvert.convertEpub(work, epub_file_full_path, mobi_file_full_path)

make_ebooks.short_description = "Recreate ebook"

# A command to make references to related works
def make_related_works(modeladmin, request, queryset):

    count_made = 0

    for work in queryset:
        related_works = RelatedWork.find_related_for_work(work)

        count_made += len(related_works)

    modeladmin.message_user(request, "%i work references discovered" % count_made)

make_related_works.short_description = "Auto-link related works"

class WorkAdmin(admin.ModelAdmin):
    
    #prepopulated_fields = {"title_slug": ("title",)}
    
    list_display = ('title', 'language', 'work_type', 'title_slug')
    list_editable = ('work_type',)
    list_filter = ('language', 'work_type', 'authors')
    search_fields = ('title',)

    actions = [make_search_indexes, make_ebooks, make_related_works]

    fieldsets = (
        (None, {
            'fields': ( ('title', 'title_slug'), 'language', 'work_type', ('authors', 'editors'), 'descriptor', 'date_written'),
        }),
    )
    
    inlines = [
        DivisionInline,
    ]

admin.site.register(Work, WorkAdmin)

class WorkTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(WorkType, WorkTypeAdmin)

admin.site.register(Division, DivisionModel)

class WordFormInline(admin.StackedInline):
    model = WordForm
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ('form', ),
        }),
    )

class LemmaAdmin(admin.ModelAdmin):
    
    list_display = ('lexical_form', 'reference_number')
    search_fields = ('lexical_form',)

admin.site.register(Lemma, LemmaAdmin)

class WordDescriptionInline(admin.StackedInline):
    model = WordDescription
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ( ('meaning', ), ('person', 'number', 'part_of_speech'), 'dialects', ('indeclinable', 'particle'), 'description'),
        }),
        ('Nouns', {
            'fields': ( ('masculine', 'feminine', 'neuter', 'geog_name', 'numeral'), 'cases'),
        }),
        ('Verbs', {
            'fields': ( ('voice', 'mood', 'tense'), ('adverb', 'infinitive', 'participle',)  ),
        }),
        ('Other', {
            'fields': ( ('superlative', 'comparative', 'expletive'), ('poetic', 'clitic', 'movable_nu' ) ),
        })
    ) 

class WordFormModel(admin.ModelAdmin):
    
    search_fields = ['form']
    list_display = ('form', 'basic_form')
    
    fieldsets = (
        (None, {
            'fields': ('form', 'basic_form'),
        }),
    )
    
    inlines = [
        WordDescriptionInline,
    ]
    
admin.site.register(WordForm, WordFormModel)

class WordDescriptionModel(admin.ModelAdmin):
    model = WordDescription
    
    search_fields = ['meaning', 'description',]
    list_display = ('word_form', '__unicode__', 'part_of_speech', 'meaning')
    list_filter = ('part_of_speech', 'geog_name', 'voice')
    
    fieldsets = (
        (None, {
            'fields': ( ('meaning', ), ('person', 'number', 'part_of_speech'), 'dialects', ('indeclinable', 'particle'), 'description'),
        }),
        ('Nouns', {
            'fields': ( ('masculine', 'feminine', 'neuter', 'geog_name', 'numeral'), 'cases'),
        }),
        ('Verbs', {
            'fields': ( ('voice', 'mood', 'tense'), ('adverb', 'infinitive', 'participle',)  ),
        }),
        ('Other', {
            'fields': ( ('superlative', 'comparative', 'expletive'), ('poetic', 'clitic', 'movable_nu' ) ),
        })
    ) 

admin.site.register(WordDescription, WordDescriptionModel)

class WikiArticleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('search', 'article'),
        }),
    )

admin.site.register(WikiArticle, WikiArticleAdmin)