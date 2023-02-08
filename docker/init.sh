#!/bin/bash

# Switch to postgres user
if [ "$(id -u)" = '0' ]; then
    chown -R postgres /var/lib/postgresql/data
    exec gosu postgres "$0" "$@"
fi

# Run the original command
exec "$@"