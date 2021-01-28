#!/bin/bash
set -e

bash /app/scripts/wait-for-db.sh

echo "Starting bot..."
exec python main.py
