ARG PYTHON_VERSION=3.12-slim-bookworm


FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN mkdir -p /app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock README.md /app/

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY . /app/

ENV PATH="/app/.venv/bin:$PATH"

ENV SECRET_KEY "non-secret-key-for-building-purposes"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "company_x_backend.wsgi"]