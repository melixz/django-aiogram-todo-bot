FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .
RUN uv pip install --system \
    django>=5.1 \
    djangorestframework>=3.15 \
    django-ulid>=0.0.4 \
    ulid>=1.1.0 \
    celery>=5.4 \
    redis>=5.2 \
    django-celery-beat>=2.7 \
    "psycopg[binary]>=3.2" \
    httpx>=0.28 \
    django-cors-headers>=4.6 \
    gunicorn>=23.0

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "config.wsgi:application"]
