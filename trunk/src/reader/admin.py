from reader.models import Author, Work, WorkType, Division, Verse, Lemma, WordForm, WordDescription
from django.contrib import admin

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
            'fields': ( ('descriptor', 'sequence_number'), ('title', 'subtitle'), 'original_content'),
        }),
    )

class WorkAdmin(admin.ModelAdmin):
    
    #prepopulated_fields = {"title_slug": ("title",)}
    
    list_display = ('title', 'language', 'work_type', 'title_slug')
    list_editable = ('work_type',)
    list_filter = ('language', 'work_type', 'authors')
    search_fields = ('title',)
    
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
    
    search_fields = ('form',),
    
    fieldsets = (
        (None, {
            'fields': ('form', ),
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