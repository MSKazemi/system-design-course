#!/bin/sh
# Runs once, on first start of the primary (docker-entrypoint-initdb.d).
set -eu

psql -v ON_ERROR_STOP=1 -U postgres -d lumen <<SQL
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD '${REPLICATION_PASSWORD}';
CREATE TABLE events (
    id         bigserial PRIMARY KEY,
    note       text        NOT NULL,
    written_at timestamptz NOT NULL DEFAULT now()
);
SQL

# Allow streaming replication connections from the compose network (lab only).
echo "host replication replicator all scram-sha-256" >> "$PGDATA/pg_hba.conf"
