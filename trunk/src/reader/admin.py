from reader.models import Author, Work, WorkSource, WorkType, Division, Verse
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
    
    list_display = ('work', 'descriptor', 'sequence_number', 'title', 'type', 'level', 'readable_unit')
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
            'fields': ( ('title', 'title_slug'), 'language', 'work_type', ('authors', 'translators'), 'descriptor', 'date_written'),
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
