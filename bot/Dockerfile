FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .

RUN uv pip install --system aiogram>=3.15 aiogram-dialog>=2.2 httpx>=0.28 pydantic-settings>=2.6

COPY . .

CMD ["python", "main.py"]
