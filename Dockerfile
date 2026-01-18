FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-root

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "nasi_ayam.main"]
