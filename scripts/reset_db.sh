#!/bin/bash
set -e

source .env

echo "WARNING: This will drop and recreate the database!"
read -p "Continue? (y/N) " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted"
    exit 0
fi

mysql -h "${MYSQL_HOST:-localhost}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" << SQL
DROP DATABASE IF EXISTS ${MYSQL_DATABASE};
CREATE DATABASE ${MYSQL_DATABASE};
SQL

echo "Database reset. Run setup to reinitialize."
