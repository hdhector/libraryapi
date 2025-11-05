from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from .models import Author, Book

User = get_user_model()


class AuthorModelTest(TestCase):
    """Pruebas unitarias para el modelo Author."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.author_data = {
            'first_name': 'Augusto',
            'last_name': 'Roa Bastos',
            'birth_date': date(1917, 6, 13),
            'nationality': 'Paraguay',
            'biography': 'Escritor paraguayo, ganador del premio cervantes en 1989.'
        }
    
    def test_create_author(self):
        """Prueba la creación de un autor."""
        author = Author.objects.create(**self.author_data)
        self.assertIsNotNone(author.id)
        self.assertEqual(author.first_name, 'Augusto')
        self.assertEqual(author.last_name, 'Roa Bastos')
        self.assertEqual(author.nationality, 'Paraguay')
        self.assertIsNotNone(author.created_at)
        self.assertIsNotNone(author.updated_at)
    
    def test_author_str(self):
        """Prueba el método __str__ del modelo Author."""
        author = Author.objects.create(**self.author_data)
        expected = f"{author.first_name} {author.last_name}"
        self.assertEqual(str(author), expected)
    
    def test_author_full_name(self):
        """Prueba la propiedad full_name del modelo Author."""
        author = Author.objects.create(**self.author_data)
        expected = f"{author.first_name} {author.last_name}"
        self.assertEqual(author.full_name, expected)
    
    def test_author_without_optional_fields(self):
        """Prueba la creación de un autor sin campos opcionales."""
        minimal_data = {
            'first_name': 'Julio',
            'last_name': 'Correa'
        }
        author = Author.objects.create(**minimal_data)
        self.assertIsNotNone(author.id)
        self.assertIsNone(author.birth_date)
        self.assertEqual(author.nationality, '')
        self.assertEqual(author.biography, '')
    
    def test_author_ordering(self):
        """Prueba el ordenamiento por defecto de los autores."""
        author1 = Author.objects.create(first_name='Manuel', last_name='Ortiz Guerrero')
        author2 = Author.objects.create(first_name='Josefina', last_name='Pla')
        author3 = Author.objects.create(first_name='Julio', last_name='Correa')
        
        authors = list(Author.objects.all())
        # Ordenamiento por last_name, first_name
        self.assertEqual(authors[0].last_name, 'Correa')
        self.assertEqual(authors[1].last_name, 'Ortiz Guerrero')
        self.assertEqual(authors[2].last_name, 'Pla')


class BookModelTest(TestCase):
    """Pruebas unitarias para el modelo Book."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.author1 = Author.objects.create(
            first_name='Gabriel',
            last_name='García Márquez',
            nationality='Colombia'
        )
        self.author2 = Author.objects.create(
            first_name='Isabel',
            last_name='Allende',
            nationality='Chile'
        )
        
        self.book_data = {
            'title': 'Cien años de soledad',
            'publication_date': date(1967, 5, 30),
            'description': 'Una novela sobre la familia Buendía.',
            'page_count': 471,
            'language': Book.Language.SPANISH
        }
    
    def test_create_book(self):
        """Prueba la creación de un libro."""
        book = Book.objects.create(**self.book_data)
        book.authors.add(self.author1)
        
        self.assertIsNotNone(book.id)
        self.assertEqual(book.title, 'Cien años de soledad')
        self.assertEqual(book.language, Book.Language.SPANISH)
        self.assertEqual(book.page_count, 471)
        self.assertIn(self.author1, book.authors.all())
        self.assertIsNotNone(book.created_at)
        self.assertIsNotNone(book.updated_at)
    
    def test_book_str(self):
        """Prueba el método __str__ del modelo Book."""
        book = Book.objects.create(**self.book_data)
        self.assertEqual(str(book), 'Cien años de soledad')
    
    def test_book_with_multiple_authors(self):
        """Prueba la relación ManyToMany entre Book y Author."""
        book = Book.objects.create(**self.book_data)
        book.authors.add(self.author1, self.author2)
        
        self.assertEqual(book.authors.count(), 2)
        self.assertIn(self.author1, book.authors.all())
        self.assertIn(self.author2, book.authors.all())
    
    def test_book_get_authors_display(self):
        """Prueba el método get_authors_display del modelo Book."""
        book = Book.objects.create(**self.book_data)
        book.authors.add(self.author1, self.author2)
        
        authors_display = book.get_authors_display()
        self.assertIn('Gabriel García Márquez', authors_display)
        self.assertIn('Isabel Allende', authors_display)
    
    def test_book_without_optional_fields(self):
        """Prueba la creación de un libro sin campos opcionales."""
        minimal_data = {
            'title': 'Libro sin detalles',
            'language': Book.Language.ENGLISH
        }
        book = Book.objects.create(**minimal_data)
        self.assertIsNotNone(book.id)
        self.assertIsNone(book.publication_date)
        self.assertEqual(book.description, '')
        self.assertIsNone(book.page_count)
    
    def test_book_default_language(self):
        """Prueba el idioma por defecto de un libro."""
        book = Book.objects.create(title='Test Book')
        self.assertEqual(book.language, Book.Language.ENGLISH)
    
    def test_book_ordering(self):
        """Prueba el ordenamiento por defecto de los libros."""
        book1 = Book.objects.create(title='Yo el supremo', language=Book.Language.SPANISH)
        book2 = Book.objects.create(title='El trueno entre las hojas', language=Book.Language.SPANISH)
        book3 = Book.objects.create(title='Madame Sui', language=Book.Language.SPANISH)
        
        books = list(Book.objects.all())
        # Ordenamiento por title
        self.assertEqual(books[0].title, 'El trueno entre las hojas')
        self.assertEqual(books[1].title, 'Madame Sui')
        self.assertEqual(books[2].title, 'Yo el supremo')
    
    def test_book_author_relationship(self):
        """Prueba la relación inversa entre Author y Book."""
        book1 = Book.objects.create(title='Libro 1', language=Book.Language.SPANISH)
        book2 = Book.objects.create(title='Libro 2', language=Book.Language.SPANISH)
        
        book1.authors.add(self.author1)
        book2.authors.add(self.author1)
        
        # Verificar que el autor puede acceder a sus libros
        self.assertEqual(self.author1.books.count(), 2)
        self.assertIn(book1, self.author1.books.all())
        self.assertIn(book2, self.author1.books.all())




class AuthorAPITest(APITestCase):
    """Pruebas de API para los endpoints de Author."""
    
    def setUp(self):
        """Configuración inicial para las pruebas de API."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Obtener token JWT
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        self.author_data = {
            'first_name': 'Augusto',
            'last_name': 'Roa Bastos',
            'birth_date': '1917-06-13',
            'nationality': 'Paraguay',
            'biography': 'Escritor paraguayo.'
        }
    
    def test_list_authors(self):
        """Prueba el endpoint de listado de autores."""
        Author.objects.create(
            first_name='Augusto',
            last_name='Roa Bastos',
            nationality='Paraguay'
        )
        Author.objects.create(
            first_name='Gabriel',
            last_name='García Márquez',
            nationality='Colombia'
        )
        
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_author(self):
        """Prueba la creación de un autor mediante API."""
        response = self.client.post(reverse('author-list'), self.author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 1)
        self.assertEqual(response.data['first_name'], 'Augusto')
        self.assertEqual(response.data['last_name'], 'Roa Bastos')
        self.assertEqual(response.data['full_name'], 'Augusto Roa Bastos')
        self.assertEqual(response.data['nationality'], 'Paraguay')
        self.assertIn('books_count', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
    
    def test_retrieve_author(self):
        """Prueba la obtención de un autor específico."""
        author = Author.objects.create(**{
            'first_name': 'Augusto',
            'last_name': 'Roa Bastos',
            'nationality': 'Paraguay'
        })
        book1 = Book.objects.create(title='Libro 1', language=Book.Language.SPANISH)
        book2 = Book.objects.create(title='Libro 2', language=Book.Language.SPANISH)
        author.books.add(book1, book2)
        
        response = self.client.get(reverse('author-detail', kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Augusto')
        self.assertEqual(response.data['full_name'], 'Augusto Roa Bastos')
        self.assertIn('books', response.data)  # Detail serializer incluye libros
        self.assertEqual(len(response.data['books']), 2)
    
    def test_update_author(self):
        """Prueba la actualización completa de un autor."""
        author = Author.objects.create(**{
            'first_name': 'Augusto',
            'last_name': 'Roa Bastos',
            'nationality': 'Paraguay'
        })
        
        update_data = {
            'first_name': 'Augusto',
            'last_name': 'Roa Bastos',
            'nationality': 'España',
            'biography': 'Biografía actualizada'
        }
        
        response = self.client.put(
            reverse('author-detail', kwargs={'pk': author.id}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        author.refresh_from_db()
        self.assertEqual(author.nationality, 'España')
    
    def test_partial_update_author(self):
        """Prueba la actualización parcial de un autor."""
        author = Author.objects.create(**{
            'first_name': 'Augusto',
            'last_name': 'Roa Bastos',
            'nationality': 'Paraguay'
        })
        
        response = self.client.patch(
            reverse('author-detail', kwargs={'pk': author.id}),
            {'nationality': 'España'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        author.refresh_from_db()
        self.assertEqual(author.nationality, 'España')
        self.assertEqual(author.first_name, 'Augusto')  # No cambió
    
    def test_delete_author(self):
        """Prueba la eliminación de un autor."""
        author = Author.objects.create(**{
            'first_name': 'Augusto',
            'last_name': 'Roa Bastos',
            'nationality': 'Paraguay'
        })
        
        response = self.client.delete(reverse('author-detail', kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), 0)
    
    def test_author_statistics(self):
        """Prueba el endpoint de estadísticas de autor."""
        author = Author.objects.create(
            first_name='Augusto',
            last_name='Roa Bastos',
            nationality='Paraguay'
        )
        book1 = Book.objects.create(
            title='Yo el supremo',
            language=Book.Language.SPANISH,
            page_count=500
        )
        book2 = Book.objects.create(
            title='El trueno entre las hojas',
            language=Book.Language.SPANISH,
            page_count=300
        )
        author.books.add(book1, book2)
        
        response = self.client.get(reverse('author-statistics', kwargs={'pk': author.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('author', response.data)
        self.assertIn('statistics', response.data)
        self.assertIn('total_books', response.data['statistics'])
        self.assertEqual(response.data['statistics']['total_books'], 2)
        self.assertIn('books_by_language', response.data)
        self.assertIn('books_by_decade', response.data)
        self.assertIn('recent_books', response.data)


class BookAPITest(APITestCase):
    """Pruebas de API para los endpoints de Book."""
    
    def setUp(self):
        """Configuración inicial para las pruebas de API."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Obtener token JWT
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        self.author = Author.objects.create(
            first_name='Augusto',
            last_name='Roa Bastos',
            nationality='Paraguay'
        )
        
        self.book_data = {
            'title': 'Yo el supremo',
            'publication_date': '1974-01-01',
            'description': 'Novela de Augusto Roa Bastos',
            'page_count': 500,
            'language': 'es',
            'authors_ids': [self.author.id]
        }
    
    def test_list_books(self):
        """Prueba el endpoint de listado de libros."""
        Book.objects.create(
            title='Yo el supremo',
            language=Book.Language.SPANISH
        )
        Book.objects.create(
            title='El trueno entre las hojas',
            language=Book.Language.SPANISH
        )
        
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_book(self):
        """Prueba la creación de un libro mediante API."""
        response = self.client.post(reverse('book-list'), self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(response.data['title'], 'Yo el supremo')
        self.assertEqual(response.data['language'], 'es')
        self.assertEqual(response.data['language_display'], 'Spanish')
        self.assertEqual(response.data['page_count'], 500)
        self.assertEqual(len(response.data['authors']), 1)
        self.assertEqual(response.data['authors_count'], 1)
        self.assertIn('created_at', response.data)
    
    def test_retrieve_book(self):
        """Prueba la obtención de un libro específico."""
        author2 = Author.objects.create(
            first_name='Gabriel',
            last_name='García Márquez',
            nationality='Colombia'
        )
        book = Book.objects.create(
            title='Yo el supremo',
            language=Book.Language.SPANISH
        )
        book.authors.add(self.author, author2)
        
        response = self.client.get(reverse('book-detail', kwargs={'pk': book.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Yo el supremo')
        self.assertIn('authors', response.data)
        self.assertEqual(len(response.data['authors']), 2)
        # Verificar que los autores tienen información completa en detail serializer
        self.assertIn('first_name', response.data['authors'][0])
        self.assertIn('nationality', response.data['authors'][0])
    
    def test_update_book(self):
        """Prueba la actualización completa de un libro."""
        book = Book.objects.create(
            title='Yo el supremo',
            language=Book.Language.SPANISH
        )
        book.authors.add(self.author)
        
        update_data = {
            'title': 'El trueno entre las hojas',
            'language': 'es',
            'page_count': 300,
            'authors_ids': [self.author.id]
        }
        
        response = self.client.put(
            reverse('book-detail', kwargs={'pk': book.id}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, 'El trueno entre las hojas')
    
    def test_partial_update_book(self):
        """Prueba la actualización parcial de un libro."""
        book = Book.objects.create(
            title='Yo el supremo',
            language=Book.Language.SPANISH
        )
        
        response = self.client.patch(
            reverse('book-detail', kwargs={'pk': book.id}),
            {'page_count': 600},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.page_count, 600)
        self.assertEqual(book.title, 'Yo el supremo')  # No cambió
    
    def test_delete_book(self):
        """Prueba la eliminación de un libro."""
        book = Book.objects.create(
            title='Yo el supremo',
            language=Book.Language.SPANISH
        )
        
        response = self.client.delete(reverse('book-detail', kwargs={'pk': book.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
    
    def test_unauthenticated_access(self):
        """Prueba que los endpoints requieren autenticación."""
        self.client.credentials()  # Remover autenticación
        
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
