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
echo "Host: 0.0.0.0"
echo "App: app.main:app"
echo "Python path: $PYTHONPATH"
echo "Working directory: $(pwd)"

# Verify uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "⚠️  uvicorn not found in PATH, using python -m uvicorn"
    UVICORN_CMD="python -m uvicorn"
else
    echo "✅ uvicorn found in PATH"
    UVICORN_CMD="uvicorn"
fi

# Use python -m uvicorn for better reliability
# Add --log-level info for better debugging
# Use --timeout-keep-alive to prevent connection issues
echo "Executing: $UVICORN_CMD app.main:app --host 0.0.0.0 --port $PORT --log-level info"
exec $UVICORN_CMD app.main:app --host 0.0.0.0 --port $PORT --log-level info --timeout-keep-alive 30

