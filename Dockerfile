FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install kafka-python pandas minio psycopg2-binary pyarrow