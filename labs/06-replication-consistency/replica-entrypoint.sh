#!/bin/sh
# Replica bootstrap: clone the primary with pg_basebackup on first start, then run as a hot standby.
#   -R  writes standby.signal + primary_conninfo, so the server starts in recovery and streams WAL
#   -C -S replica1  creates a physical replication slot so the primary keeps WAL the replica still needs
set -eu
export PGDATA=/var/lib/postgresql/18/docker

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "replica: cloning primary..."
  until pg_isready -h primary -U postgres -q; do sleep 1; done
  mkdir -p "$PGDATA"
  pg_basebackup \
    -d "host=primary user=replicator password=${REPLICATION_PASSWORD} application_name=replica1" \
    -D "$PGDATA" -R -X stream -C -S replica1 -P
  chmod 700 "$PGDATA"
fi

exec postgres -c hot_standby=on
