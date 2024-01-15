FROM python:3.8

RUN apt-get update  \
    && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app
