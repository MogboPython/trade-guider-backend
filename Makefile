ifneq (,$(wildcard ./.env))
    include .env
    export
endif

backend-dev:
	@echo "creating & running migrations..."
	poetry run python manage.py makemigrations && poetry run python manage.py migrate

	@echo "starting librarian server..."
	poetry run python manage.py runserver 127.0.0.1:8000

backend-migrations:
	@echo "creating & running migrations..."
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

test-backend:
	@echo "Running tests"
	poetry run python manage.py test users/