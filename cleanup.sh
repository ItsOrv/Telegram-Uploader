#!/bin/bash

echo "Cleaning up..."
find . -name "*.session" -delete
find . -name "*.session-journal" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
echo "Done"
