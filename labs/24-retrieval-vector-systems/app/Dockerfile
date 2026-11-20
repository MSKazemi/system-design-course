FROM python:3.12-slim
# Pinned client dependencies (latest stable on 2026-11-19)
RUN pip install --no-cache-dir "psycopg[binary]==3.3.9" "numpy==2.5.5"
WORKDIR /app
COPY . /app
