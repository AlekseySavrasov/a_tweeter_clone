FROM python:3.8

RUN apt-get update  \
    && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /myapp/
RUN pip install -r /myapp/requirements.txt

COPY . /myapp

WORKDIR /myapp
