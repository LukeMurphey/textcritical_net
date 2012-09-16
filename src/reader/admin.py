from reader.models import Author, Work, WorkSource, WorkType, Chapter
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

class WorkAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'language')
    
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