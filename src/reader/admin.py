from reader.models import Author, Work, WorkSource, WorkType, Chapter, Verse, Section
from django.contrib import admin

class AuthorAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'date_born', 'date_died', 'meta_author'),
        }),
    )

admin.site.register(Author, AuthorAdmin)

class ChapterInline(admin.StackedInline):
    model = Chapter
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ( ('descriptor', 'sequence_number'), ('title', 'subtitle'), 'original_content'),
        }),
    )

class WorkAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'language', 'work_type')
    list_editable = ('work_type',)
    list_filter = ('language', 'work_type', 'authors')
    search_fields = ('title',)
    
    fieldsets = (
        (None, {
            'fields': ( ('title', 'language'), 'work_type', ('authors', 'translators'), 'descriptor', 'date_written'),
        }),
    )
    
    inlines = [
        ChapterInline,
    ]

admin.site.register(Work, WorkAdmin)

class WorkTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(WorkType, WorkTypeAdmin)

class VerseInline(admin.StackedInline):
    model = Verse
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ( ('indicator', 'sequence_number'), 'content', 'original_content'),
        }),
    )

class ChapterModel(admin.ModelAdmin):
    
    list_display = ('work', 'descriptor', 'sequence_number')
    list_filter = ('work', )
    search_fields = ('original_content',)
    
    inlines = [
        VerseInline,
    ]
    
admin.site.register(Chapter, ChapterModel)

class SectionModel(admin.ModelAdmin):
    
    list_display = ('title', 'type', 'level')
    list_filter = ('level', 'type',)
    search_fields = ('title',)
    
admin.site.register(Section, SectionModel)