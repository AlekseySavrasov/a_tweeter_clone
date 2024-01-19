FROM python:3.10 as development

WORKDIR /app

COPY requirements-dev.txt /app/
RUN pip install -r /app/requirements-dev.txt

COPY . /app

FROM python:3.10-slim as production

RUN apt-get update  \
    && apt-get install -y nginx \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=development /app /app

COPY requirements-prod.txt /app/
RUN pip install -r /app/requirements-prod.txt

ENV APP_ENV=production
