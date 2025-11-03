from django.core.management.base import BaseCommand
from django.db.models import Count
from library.models import Author, Book
from faker import Faker
import random


class Command(BaseCommand):
    """Comando para generar datos de prueba: autores y libros con relaciones usando Faker."""
    help = "Carga datos de prueba (autores y libros) usando Faker"

    def handle(self, *args, **options):
        """Genera autores y libros con datos aleatorios en espanol."""
        fake = Faker("es_ES")  # Generador de datos falsos en espanol
        Faker.seed(42)  # Para reproducibilidad

        num_authors = 10
        num_books = 30

        self.stdout.write(self.style.MIGRATE_HEADING("Generando datos de prueba..."))

        # --- Crear autores ---
        authors = []
        nationalities = ['Paraguay', 'España', 'Mexico', 'Argentina', 'Colombia', 'Chile', 
                        'Brasil', 'Estados Unidos', 'Reino Unido', 'Francia', 'Alemania']
        
        for _ in range(num_authors):
            # Fecha de nacimiento entre 1900 y 2000
            birth_date = fake.date_between(start_date='-120y', end_date='-25y')
            
            author = Author.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                birth_date=birth_date,
                nationality=random.choice(nationalities),
                biography=fake.text(max_nb_chars=500),
            )
            authors.append(author)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {len(authors)} autores creados."))

        # --- Crear libros ---
        languages = [Book.Language.SPANISH, Book.Language.ENGLISH, 
                    Book.Language.FRENCH, Book.Language.GERMAN, 
                    Book.Language.PORTUGUESE, Book.Language.OTHER]
        
        # Plantillas para generar titulos
        title_prefixes = [
            "El", "La", "Los", "Las", "Un", "Una", "Historia de", 
            "Crónicas de", "Memorias de", "Viaje a", "El misterio de",
            "El secreto de", "La vida de", "Aventuras en", "El legado de"
        ]
        
        title_suffixes = [
            "perdido", "olvidado", "oculto", "rojo", "azul", "dorado",
            "oscuro", "brillante", "eterno", "final", "primero", "último",
            "secreto", "misterioso", "legendario", "extraordinario"
        ]

        books = []
        for _ in range(num_books):
            # Seleccionar 1-3 autores aleatorios para cada libro
            num_book_authors = random.randint(1, min(3, len(authors)))
            book_authors = random.sample(authors, num_book_authors)
            
            # Generar titulo variado
            title_type = random.choice(['simple', 'with_prefix', 'with_suffix', 'full', 'sentence'])
            
            if title_type == 'simple':
                # Titulo simple: "El misterio"
                title = random.choice(title_prefixes)
            elif title_type == 'with_prefix':
                # Titulo con prefijo: "El misterio de [lugar/persona]"
                prefix = random.choice(title_prefixes)
                if random.choice([True, False]):
                    title = f"{prefix} {fake.city()}"
                else:
                    title = f"{prefix} {fake.first_name()}"
            elif title_type == 'with_suffix':
                # Titulo con sufijo: "[Sustantivo] [sufijo]"
                noun = fake.word().capitalize()
                suffix = random.choice(title_suffixes)
                title = f"{noun} {suffix}"
            elif title_type == 'full':
                # Titulo completo: "El [sustantivo] de [lugar]"
                prefix = random.choice(title_prefixes)
                place = fake.city() if random.choice([True, False]) else fake.country()
                title = f"{prefix} {fake.word().capitalize()} de {place}"
            else:  # sentence
                # Titulo como oracion: "Cuando [algo] sucedio"
                title = fake.sentence(nb_words=random.randint(3, 8)).rstrip('.')
            
            # Asegurar que no exceda max_length=250
            title = title[:250]
            
            # Fecha de publicación entre 1950 y 2024
            publication_date = fake.date_between(start_date='-74y', end_date='today')
            
            book = Book.objects.create(
                title=title,
                publication_date=publication_date,
                description=fake.text(max_nb_chars=300),
                page_count=random.randint(100, 800),
                language=random.choice(languages),
            )
            
            # Asignar autores al libro
            book.authors.set(book_authors)
            books.append(book)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {len(books)} libros creados."))
        
        # --- Resumen ---
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("Resumen de datos generados:"))
        self.stdout.write(self.style.SUCCESS(f"  Autores: {Author.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Libros: {Book.objects.count()}"))
        books_without_authors = Book.objects.annotate(author_count=Count('authors')).filter(author_count=0).count()
        self.stdout.write(self.style.SUCCESS(f"  Libros sin autores: {books_without_authors}"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(self.style.SUCCESS("\nDatos de prueba cargados exitosamente!"))

