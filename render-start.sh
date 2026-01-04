#!/bin/bash
# Render startup script for backend
# This script runs database migrations before starting the server

set -e

echo "Starting backend pre-start checks..."

# Validate database configuration first
echo "Validating database configuration..."
cd /app
python -m app.scripts.validate_db_config || {
    echo "❌ Database configuration validation failed!"
    echo "Please check the error message above and update SUPABASE_DB_URL in Render environment variables."
    exit 1
}

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Run any initialization scripts if needed
# python -m app.initial_data

echo "Pre-start checks completed. Starting server..."

# Start the backend server
exec fastapi run --host 0.0.0.0 --port ${PORT:-8000} app/main.py
