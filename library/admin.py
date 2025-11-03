from django.contrib import admin
from .models import Author, Book


class BookInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1


class AuthorInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'nationality', 'birth_date', 'created_at']
    list_filter = ['nationality', 'birth_date']
    search_fields = ['first_name', 'last_name', 'biography']
    ordering = ['last_name', 'first_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BookInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'publication_date', 'language', 'page_count', 'get_authors_display']
    list_filter = ['language', 'publication_date', 'authors']
    search_fields = ['title', 'description']
    filter_horizontal = ['authors']
    ordering = ['title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AuthorInline]
    
    def get_authors_display(self, obj):
        return obj.get_authors_display()
    get_authors_display.short_description = 'Authors'
