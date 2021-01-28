#!/bin/bash

HOST="${MYSQL_HOST:-db}"
PORT="${MYSQL_PORT:-3306}"
MAX=30

echo "Waiting for MySQL at $HOST:$PORT..."
for i in $(seq 1 $MAX); do
    if mysqladmin ping -h "$HOST" -P "$PORT" --silent 2>/dev/null; then
        echo "MySQL is up"
        exit 0
    fi
    echo "  attempt $i/$MAX..."
    sleep 2
done

echo "MySQL not ready after $MAX attempts"
exit 1
