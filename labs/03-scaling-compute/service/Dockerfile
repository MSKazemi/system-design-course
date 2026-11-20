FROM python:3.15.2-slim
WORKDIR /app
COPY app.py .
USER nobody
EXPOSE 8080
CMD ["python", "-u", "app.py"]
