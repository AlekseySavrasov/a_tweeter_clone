FROM python:3.8 as development

WORKDIR /app

COPY requirements-dev.txt /app/

RUN pip install -r /app/requirements-dev.txt

FROM python:3.8-slim as production

RUN apt-get update  \
    && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt /app/
RUN pip install -r /app/requirements-prod.txt

COPY . /app

WORKDIR /app

ENV APP_ENV=production
