from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import AuthorViewSet, BookViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)), # URLS para el router /api/authors/ y /api/books/
]

