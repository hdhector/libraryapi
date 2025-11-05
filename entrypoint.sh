#!/bin/bash
set -euo pipefail

echo "Starting Library API setup..."

# Docker Compose ya carga las variables del env_file, pero si no están definidas,
# intentamos cargarlas desde .env (útil para desarrollo local sin docker-compose)
# Solo cargamos si las variables críticas no están ya definidas
if [ -z "${POSTGRES_HOST:-}" ] && [ -f .env ]; then
  echo "Loading environment variables from .env (Docker Compose no detectado)..."
  set -o allexport; source .env; set +o allexport
fi

# Usar valores por defecto para desarrollo local
export POSTGRES_HOST=${POSTGRES_HOST:-db}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_USER=${POSTGRES_USER:-postgres}
export POSTGRES_DB=${POSTGRES_DB:-libraryapi}

# Esperar a que la base de datos esté disponible
echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Ejecutar migraciones
echo "Applying database migrations..."
python manage.py migrate --noinput

# Crear superusuario automáticamente si no existe
echo "Checking superuser existence..."
python - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
u = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
e = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
p = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
    print(f"Superuser created: {u}")
else:
    print(f"Superuser already exists: {u}")
PY

# Recolectar archivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Lanzar servidor Django
echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000