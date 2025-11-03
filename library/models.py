from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['nationality']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    class Language(models.TextChoices):
        SPANISH = 'es', 'Spanish'
        ENGLISH = 'en', 'English'
        FRENCH = 'fr', 'French'
        GERMAN = 'ge', 'German'
        PORTUGUESE = 'pt', 'Portuguese'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=250)
    publication_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        default=Language.ENGLISH
    )
    authors = models.ManyToManyField(Author, related_name='books')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return self.title

    def get_authors_display(self):
        return ', '.join([author.full_name for author in self.authors.all()])
