FROM python:3.15.2-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir "psycopg[binary]==3.3.9" "redis==8.1.0"
WORKDIR /lab
COPY bench.py .
ENTRYPOINT ["python3", "bench.py"]
CMD ["--help"]
