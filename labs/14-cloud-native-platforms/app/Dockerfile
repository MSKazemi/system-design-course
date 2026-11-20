FROM python:3.15.2-slim-trixie
ARG APP_VERSION=v1
ENV APP_VERSION=${APP_VERSION}
RUN useradd --uid 10001 --no-create-home app
WORKDIR /srv
COPY server.py client.py .
USER 10001
EXPOSE 8080
CMD ["python", "-u", "server.py"]
