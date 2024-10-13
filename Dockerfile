FROM python:3.12-slim-bookworm

RUN apt update && apt install -y make curl

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock Makefile /app/
RUN touch README.md

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
# RUN poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY companyXbackend /app/companyXbackend

ENV PATH="/app/.venv/bin:$PATH"

# ENTRYPOINT []

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "companyXbackend.wsgi"]
# CMD ["python", "companyXbackend/manage.py", "migrate", "--noinput"]