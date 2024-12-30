FROM python:3.12.8-alpine3.21

ENV PYTHOUNNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN apk add --no-cache jpeg-dev zlib-dev

RUN apk add --no-cache --virtual .build-deps build-base linux-headers

RUN pip install poetry

COPY . .

RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user
   
RUN mkdir /home/django-user

RUN chown -R django-user /home/django-user

RUN chmod -R 755 /home/django-user

USER django-user

RUN poetry install
