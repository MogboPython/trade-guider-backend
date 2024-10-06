ifneq (,$(wildcard ./.env))
    include .env
    export
endif

backend-dev:
	@echo "creating & running migrations..."
	poetry run python companyXbackend/manage.py makemigrations && poetry run python companyXbackend/manage.py migrate

	@echo "starting librarian server..."
	poetry run python companyXbackend/manage.py runserver 0.0.0.0:8084

backend-migrations:
	@echo "creating & running migrations..."
	poetry run python companyXbackend/manage.py makemigrations
	poetry run python companyXbackend/manage.py migrate

test-backend:
	@echo "Running tests"
	poetry run python companyXbackend/manage.py test companyXbackend/users/