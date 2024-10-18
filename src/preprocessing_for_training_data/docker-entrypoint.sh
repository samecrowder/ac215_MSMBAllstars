#!/bin/bash
set -e

echo "Starting script"
python /app/preprocess.py

exec "$@"
