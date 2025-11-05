from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import (
    Count, Avg, Q, F, Max, Min, Sum,
    Case, When, IntegerField, CharField, Value
)
from django.db.models.functions import ExtractYear, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Author, Book
from .serializers import (
    AuthorSerializer, AuthorDetailSerializer,
    BookSerializer, BookDetailSerializer
)




@extend_schema_view(
    list=extend_schema(
        summary='Listar autores',
        description='Retorna una lista paginada de autores con sus datos básicos (id, nombre, nacionalidad, biografía, cantidad de libros). Incluye información de paginación y permite filtros por nacionalidad y búsqueda por nombre.',
        tags=['Autores'],
        responses={200: {'description': 'Lista de autores'}},
    ),
    create=extend_schema(
        summary='Crear autor',
        description='Crea un nuevo autor y retorna los datos completos del autor creado incluyendo id, fechas de creación y actualización.',
        tags=['Autores'],
        responses={200: {'description': 'Autor creado exitosamente'}},
    ),
    retrieve=extend_schema(
        summary='Obtener autor',
        description='Retorna los detalles completos de un autor específico incluyendo información de sus libros (hasta 10 libros con id, título, fecha de publicación e idioma).',
        tags=['Autores'],
        responses={200: {'description': 'Detalles del autor con sus libros'}},
    ),
    update=extend_schema(
        summary='Actualizar autor',
        description='Actualiza completamente un autor y retorna los datos actualizados del autor.',
        tags=['Autores'],
        responses={200: {'description': 'Autor actualizado exitosamente'}},
    ),
    partial_update=extend_schema(
        summary='Actualizar autor parcialmente',
        description='Actualiza parcialmente un autor y retorna los datos actualizados. Solo se modifican los campos enviados.',
        tags=['Autores'],
        responses={200: {'description': 'Autor actualizado parcialmente'}},
    ),
    destroy=extend_schema(
        summary='Eliminar autor',
        description='Elimina un autor del sistema. No retorna contenido en el cuerpo de la respuesta.',
        tags=['Autores'],
        responses={204: {'description': 'Autor eliminado exitosamente'}},
    ),
)

class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar autores con CRUD completo.
    
    Incluye endpoints personalizados para estadísticas y análisis.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['nationality']
    search_fields = ['first_name', 'last_name', 'nationality', 'biography']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'updated_at']
    ordering = ['first_name', 'last_name']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'retrieve':
            return AuthorDetailSerializer
        return AuthorSerializer
    
    @extend_schema(
        summary='Estadísticas de autor',
        description='Retorna estadísticas detalladas de un autor: información básica del autor, estadísticas agregadas (total de libros, páginas promedio/máximas/mínimas/totales), agrupación de libros por idioma con conteo y promedio de páginas, agrupación por década de publicación, y lista de los 5 libros más recientes con id, título y fecha.',
        tags=['Autores', 'Estadísticas'],
        responses={200: {'description': 'Estadísticas del autor'}},
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Endpoint que retorna estadísticas detalladas de un autor específico.
        Calcula estadísticas detalladas sobre los libros del autor, incluyendo:
        - total de libros, páginas promedio, máximas, mínimas y totales,
        - agrupación de libros por idioma y década de publicación,
        - listado de los 5 libros más recientes.
        """
        author = self.get_object()
        
        # Estadísticas de libros 
        stats = author.books.aggregate(
            total_books=Count('id'),
            avg_pages=Avg('page_count'),
            max_pages=Max('page_count'),
            min_pages=Min('page_count'),
            total_pages=Sum('page_count'),
        )
        
        # Agrupar por idioma
        books_by_language = author.books.values('language').annotate(
            count=Count('id'),
            avg_pages=Avg('page_count')
        ).order_by('-count')
        
        # Agrupar por decada de publicación
        books_by_decade = author.books.annotate(
            decade=Case(
                When(publication_date__isnull=True, then=None),
                default=ExtractYear('publication_date') - ExtractYear('publication_date') % 10,
                output_field=IntegerField()
            )
        ).values('decade').annotate(
            count=Count('id')
        ).order_by('decade')
        
        # Libros más recientes
        recent_books = author.books.order_by('-publication_date')[:5].values(
            'id', 'title', 'publication_date'
        )
        
        return Response({
            'author': {
                'id': author.id,
                'full_name': author.full_name,
                'nationality': author.nationality,
            },
            'statistics': stats,
            'books_by_language': list(books_by_language),
            'books_by_decade': list(books_by_decade),
            'recent_books': list(recent_books),
        })


@extend_schema_view(
    list=extend_schema(
        summary='Listar libros',
        description='Retorna una lista paginada de libros con sus datos básicos (id, título, fecha de publicación, descripción, páginas, idioma, cantidad de autores). Incluye información de paginación y permite filtros por idioma, autor y búsqueda por título.',
        tags=['Libros'],
        responses={200: {'description': 'Lista de libros'}},
    ),
    create=extend_schema(
        summary='Crear libro',
        description='Crea un nuevo libro y retorna los datos completos del libro creado incluyendo id, autores asociados, fechas de creación y actualización.',
        tags=['Libros'],
        responses={200: {'description': 'Libro creado exitosamente'}},
    ),
    retrieve=extend_schema(
        summary='Obtener libro',
        description='Retorna los detalles completos de un libro específico incluyendo información completa de todos sus autores (id, nombre completo, nacionalidad, biografía, etc.).',
        tags=['Libros'],
        responses={200: {'description': 'Detalles del libro con información completa de autores'}},
    ),
    update=extend_schema(
        summary='Actualizar libro',
        description='Actualiza completamente un libro y retorna los datos actualizados del libro con información de sus autores.',
        tags=['Libros'],
        responses={200: {'description': 'Libro actualizado exitosamente'}},
    ),
    partial_update=extend_schema(
        summary='Actualizar libro parcialmente',
        description='Actualiza parcialmente un libro y retorna los datos actualizados. Solo se modifican los campos enviados.',
        tags=['Libros'],
        responses={200: {'description': 'Libro actualizado parcialmente'}},
    ),
    destroy=extend_schema(
        summary='Eliminar libro',
        description='Elimina un libro del sistema. No retorna contenido en el cuerpo de la respuesta.',
        tags=['Libros'],
        responses={204: {'description': 'Libro eliminado exitosamente'}},
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar libros con CRUD completo.
    
    Incluye endpoints personalizados para búsqueda avanzada y recomendaciones.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language', 'authors__id']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'publication_date', 'page_count', 'created_at']
    ordering = ['title']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookSerializer
    
    @extend_schema(
        summary='Estadísticas globales de libros',
        description='Retorna estadísticas globales: estadísticas generales (total de libros, páginas promedio/máximas/mínimas/totales), estadísticas agrupadas por idioma con conteo y promedio de páginas, estadísticas por año de publicación (últimos 20 años), libros categorizados por rango de páginas (short<100, medium<300, long<500, very_long>500, unknown), y lista de los 10 autores más libros publicados con cantidad de libros.',
        tags=['Libros', 'Estadísticas'],
        responses={200: {'description': 'Estadísticas globales de libros'}},
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Endpoint de estadísticas globales de libros.
        Usa múltiples agregaciones y consultas complejas.
        """
        queryset = self.get_queryset()
        
        # Estadísticas generales
        general_stats = queryset.aggregate(
            total_books=Count('id'),
            avg_pages=Avg('page_count'),
            max_pages=Max('page_count'),
            min_pages=Min('page_count'),
            total_pages=Sum('page_count'),
            books_with_pages=Count('id', filter=Q(page_count__isnull=False)),
        )
        
        # Estadísticas por idioma con annotate
        stats_by_language = queryset.values('language').annotate(
            count=Count('id'),
            avg_pages=Avg('page_count'),
            total_pages=Sum('page_count'),
        ).order_by('-count')
        
        # Estadísticas por año de publicación
        stats_by_year = queryset.annotate(
            year=ExtractYear('publication_date')
        ).values('year').annotate(
            count=Count('id')
        ).order_by('-year')[:20]  # Últimos 20 años
        
        # Libros por rango de páginas usando Case/When
        page_ranges = queryset.annotate(
            page_range=Case(
                When(page_count__isnull=True, then=Value('unknown')),
                When(page_count__lt=100, then=Value('short')),
                When(page_count__lt=300, then=Value('medium')),
                When(page_count__lt=500, then=Value('long')),
                default=Value('very_long'),
                output_field=CharField()
            )
        ).values('page_range').annotate(
            count=Count('id')
        )
        
        # Autores más prolíficos (top 10) que an publicado mas libros
        prolific_authors = Author.objects.annotate(
            books_count=Count('books')
        ).order_by('-books_count')[:10].values(
            'id', 'first_name', 'last_name', 'books_count'
        )
        
        return Response({
            'general_statistics': general_stats,
            'statistics_by_language': list(stats_by_language),
            'statistics_by_year': list(stats_by_year),
            'books_by_page_range': list(page_ranges),
            'most_prolific_authors': list(prolific_authors),
        })
    
    @extend_schema(
        summary='Análisis de tendencias',
        description='Retorna análisis de tendencias temporales y temáticas: tendencias por idioma a lo largo del tiempo agrupadas por década (década e idioma con conteo), crecimiento de publicaciones por década (década, conteo y promedio de páginas), y lista de autores emergentes (últimos 10 años) con cantidad de libros recientes y total de libros.',
        tags=['Libros'],
        responses={200: {'description': 'Análisis de tendencias'}},
    )
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """
        Análisis de tendencias.
        Identifica patrones temporales y temáticos.
        """
        queryset = self.get_queryset()
        
        # Tendencia por idioma a lo largo del tiempo (por década)
        language_trends = queryset.annotate(
            decade=Case(
                When(publication_date__isnull=True, then=None),
                default=ExtractYear('publication_date') - ExtractYear('publication_date') % 10,
                output_field=IntegerField()
            )
        ).values('decade', 'language').annotate(
            count=Count('id')
        ).order_by('decade', 'language')
        
        # Crecimiento de publicaciones por década
        decade_growth = queryset.annotate(
            decade=Case(
                When(publication_date__isnull=True, then=None),
                default=ExtractYear('publication_date') - ExtractYear('publication_date') % 10,
                output_field=IntegerField()
            )
        ).values('decade').annotate(
            count=Count('id'),
            avg_pages=Avg('page_count')
        ).order_by('decade')
        
        # Autores que tenga publicados libros en los ultimos 10 años
        ten_years_ago = timezone.now().date() - timedelta(days=10*365)
        emerging_authors = Author.objects.filter(
            books__publication_date__gte=ten_years_ago
        ).annotate(
            recent_books_count=Count('books', filter=Q(books__publication_date__gte=ten_years_ago)),
            total_books=Count('books')
        ).filter(recent_books_count__gt=0).order_by('-recent_books_count')[:10]
        
        emerging_authors_data = [
            {
                'id': author.id,
                'full_name': author.full_name,
                'recent_books_count': author.recent_books_count,
                'total_books': author.total_books,
            }
            for author in emerging_authors
        ]
        
        return Response({
            'language_trends': list(language_trends),
            'decade_growth': list(decade_growth),
            'emerging_authors': emerging_authors_data,
        })
