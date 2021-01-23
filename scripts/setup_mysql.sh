#!/bin/bash
set -e

DB_NAME="${MYSQL_DATABASE:-telegram_uploader}"
DB_USER="${MYSQL_USER:-telegram_user}"
DB_PASS="${MYSQL_PASSWORD:-changeme}"

mysql -u root -p"${MYSQL_ROOT_PASSWORD}" << SQL
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "MySQL setup done"
