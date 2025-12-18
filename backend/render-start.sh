#!/bin/bash
# Render startup script for backend
# This script runs database migrations before starting the server

set -e

echo "Starting backend pre-start checks..."

# Run database migrations
echo "Running database migrations..."
cd /app
python -m alembic upgrade head

# Run any initialization scripts if needed
# python -m app.initial_data

echo "Pre-start checks completed. Starting server..."

# Start the backend server using uvicorn
# Render provides PORT environment variable automatically
# Use 0.0.0.0 to bind to all interfaces (required for Render)
PORT=${PORT:-8000}
echo "Starting server on port $PORT..."

exec uvicorn app.main:app --host 0.0.0.0 --port $PORT

