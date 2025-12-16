#!/bin/sh
set -e

# Выполняем миграции и статику только при запуске веб-сервера
if [ "$1" = 'gunicorn' ]; then
    echo "Applying database migrations..."
    python manage.py migrate
    
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"

