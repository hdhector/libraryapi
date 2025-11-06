# Library API

A RESTful API built with Django and Django REST Framework for managing books and authors. Features JWT authentication, comprehensive CRUD operations and advanced filtering.

## Features

- Full CRUD operations for books and authors
- JWT authentication with Simple JWT
- Advanced filtering, search, and ordering on endpoints
- Analytics and statistics for authors and books
- Interactive API documentation using Swagger/OpenAPI (drf-spectacular)
- Docker Compose support for simplified deployment
- Deployment script included for easy production setup
- PostgreSQL database backend for reliable data storage
- Custom Django admin interface with Jazzmin theme
- Automated test suite for API endpoints and core logic
- Sample data loading scripts for quick setup and development

## Tech Stack

- Python 3.12
- Django 5.2
- Django REST Framework 3.15
- PostgreSQL 16
- Simple JWT
- drf-spectacular
- django-filter
- Docker
- Docker Compose

## Project Structure

```
libraryapi/
├── core/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── library/           # Main application
│   └── management/
│       └── commands/
│           └── load_library_data.py  # Command to load sample data
│   ├── models.py      # Author and Book models
│   ├── views.py       # ViewSets with CRUD
│   ├── serializers.py # DRF serializers
│   ├── urls.py
│   └── tests.py       # Test suite
├── docker-compose.yml # Docker configuration
├── Dockerfile         # Container definition
├── deploy.sh          # Deployment script
├── entrypoint.sh      # Docker entrypoint script
├── manage.py
├── requirements.txt
└── .env.example       # Environment variables template
```

## Installation

### Quick Start with deploy.sh

1. **Clone the repository**
   ```bash
   git clone https://github.com/hdhector/libraryapi.git
   cd libraryapi
   ```

2. **Configure environment variables (optional)**
   You can customize your environment by copying the example env file:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your preferred settings. If `.env` is not found, the application will automatically use `.env.example` as a fallback.

3. **Deploy the application**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
   
   The `deploy.sh` script automatically:
   - Builds all Docker containers
   - Applies database migrations
   - Creates a default superuser (username: `admin`, password: `admin123`)
   - Starts the application on port `8000`

The application will be available at:
- **Admin Interface**: Access the Django admin panel at `http://localhost:8000/admin/` with your superuser credentials. The admin interface features a custom Jazzmin theme for better UX.
- **API**: `http://localhost:8000/api`
- **API Documentation**: `http://localhost:8000/api/docs/`
- **Schema**: `http://localhost:8000/api/schema/`

### Additional Setup (Optional)

After deployment, you can:


**Load sample data:**
```bash
docker-compose exec web python manage.py load_library_data
```

## Testing

The project includes a comprehensive test suite with **27 tests** covering:

- **Model tests**: Validation of Author and Book models, relationships, and properties
- **API tests**: REST endpoints for authors and books including CRUD, authentication, and statistics

**Run tests:**
```bash
docker-compose exec web python manage.py test library
```

## Usage

### Main Endpoints

- **Authors**: `/api/authors/`
  - `GET /api/authors/` - List all authors
  - `POST /api/authors/` - Create new author
  - `GET /api/authors/{id}/` - Get author details
  - `PUT /api/authors/{id}/` - Update author
  - `DELETE /api/authors/{id}/` - Delete author
  - `GET /api/authors/{id}/statistics/` - Get author statistics

- **Books**: `/api/books/`
  - `GET /api/books/` - List all books
  - `POST /api/books/` - Create new book
  - `GET /api/books/{id}/` - Get book details
  - `PUT /api/books/{id}/` - Update book
  - `DELETE /api/books/{id}/` - Delete book
  - `GET /api/books/statistics/` - Get global book statistics
  - `GET /api/books/trends/` - Get trend analysis

### Filtering and Search

All list endpoints support search and ordering. Available filters vary by endpoint:

**Authors (`/api/authors/`):**
- **Filtering**: `?nationality=Paraguay` or `?birth_date=1917-06-13` (2 filters: nationality, birth_date)
- **Search**: `?search=Augusto` (searches in first_name, last_name, nationality, biography)
- **Ordering**: `?ordering=-created_at` (by id, last_name, first_name, created_at, updated_at)

**Books (`/api/books/`):**
- **Filtering**: `?language=es&authors__id=1&publication_date=1967-05-30` (3 filters: language, authors__id, publication_date)
- **Search**: `?search=1984` (searches in title, description)
- **Ordering**: `?ordering=-publication_date` (by id, title, publication_date, page_count, created_at)

**Examples:**
```bash
# Authors with nationality filter and search
GET /api/authors/?nationality=Paraguay&search=emiliano&ordering=-created_at

# Books filtered by language and author
GET /api/books/?language=es&authors__id=1&search=novel&ordering=title
```

## Author

**hdhector** - [GitHub](https://github.com/hdhector)



