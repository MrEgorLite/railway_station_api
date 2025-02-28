FROM python:3.12.8-alpine3.21

ENV PYTHOUNNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN apk add --no-cache jpeg-dev zlib-dev

RUN apk add --no-cache --virtual .build-deps build-base linux-headers

RUN pip install poetry

RUN adduser \
        --disabled-password \
        --home "/home/django-user" \
        django-user

USER django-user

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .
