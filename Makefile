.PHONY: init-dev reset-postgres psql format lint typecheck test validate

init-dev:
	pyenv install -s
	poetry install

reset-postgres:
	docker compose down
	docker volume rm nasi-ayam_postgres_data 2>/dev/null || true

psql:
	docker compose exec postgres psql -U nasi_ayam -d nasi_ayam

format:
	poetry run black nasi_ayam tests

lint:
	poetry run flake8 nasi_ayam tests

typecheck:
	poetry run mypy nasi_ayam

test:
	poetry run pytest tests/ -v

validate: format lint typecheck test
