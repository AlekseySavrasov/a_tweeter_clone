FROM python:3.7

RUN apt-get update  \
    && apt-get install -y python3-dev supervisor nginx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /myapp/
RUN pip install -r /myapp/requirements.txt

COPY . /myapp

WORKDIR /myapp

CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]