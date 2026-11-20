FROM python:3.15.2-slim
# redis-py pinned to the current stable release (PyPI, checked 2026-11-19)
RUN pip install --no-cache-dir redis==8.1.0
WORKDIR /app
COPY limiters.py run_experiments.py ./
ENTRYPOINT []
