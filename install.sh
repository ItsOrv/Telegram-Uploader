#!/bin/bash
set -e

echo "Installing Telegram Uploader Bot..."

if ! command -v python3 &>/dev/null; then
    echo "python3 not found"
    exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example - fill in your credentials"
fi

echo "Done. Run: python main.py"
