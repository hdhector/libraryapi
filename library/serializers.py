from rest_framework import serializers
from django.db.models import Count, Avg, Q
from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Author."""
    full_name = serializers.CharField(read_only=True)
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'birth_date', 'nationality', 'biography',
            'books_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_books_count(self, obj):
        """Retorna el número de libros del autor."""
        return obj.books.count()


class AuthorDetailSerializer(AuthorSerializer):
    """Serializer detallado de Author con información de libros."""
    books = serializers.SerializerMethodField()
    
    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ['books']
    
    def get_books(self, obj):
        """Retorna información básica de los libros del autor."""
        books = obj.books.all()[:10]  # Limitar a 10 libros
        return [
            {
                'id': book.id,
                'title': book.title,
                'publication_date': book.publication_date,
                'language': book.get_language_display(),
            }
            for book in books
        ]


class BookSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Book."""
    authors = AuthorSerializer(many=True, read_only=True)
    authors_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Author.objects.all(),
        source='authors',
        write_only=True,
        required=False
    )
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    authors_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'publication_date', 'description',
            'page_count', 'language', 'language_display',
            'authors', 'authors_ids', 'authors_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_authors_count(self, obj):
        """Retorna el número de autores del libro."""
        return obj.authors.count()


class BookDetailSerializer(BookSerializer):
    """Serializer detallado de Book con información completa de autores."""
    authors = AuthorSerializer(many=True, read_only=True)
    
    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields

