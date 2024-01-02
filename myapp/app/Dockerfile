FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV UVICORN_CMD="uvicorn"
ENV APP_MODULE="fastapi_app:app"
ENV HOST="0.0.0.0"
ENV PORT="5000"

CMD ["sh", "-c", "$UVICORN_CMD $APP_MODULE --host $HOST --port $PORT"]
