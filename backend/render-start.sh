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

# Test if we can import the app before starting uvicorn
echo "Testing app import..."
if ! python -c "from app.main import app; print('✅ App imported successfully')" 2>&1; then
    echo "❌ Failed to import app. Check for import errors above."
    exit 1
fi

# Use python -m uvicorn for better reliability
# Add --log-level info for better debugging
# Use --timeout-keep-alive to prevent connection issues
# Use --access-log to see all requests
echo "Executing: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info --timeout-keep-alive 30 --access-log"
echo "Server should be accessible at http://0.0.0.0:$PORT"
echo "Health check: http://0.0.0.0:$PORT/api/v1/utils/health-check"

# Use python -m uvicorn explicitly (more reliable than direct uvicorn command)
# Don't use exec so we can catch errors
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info --timeout-keep-alive 30 --access-log || {
    echo "❌ Uvicorn failed to start. Exit code: $?"
    exit 1
}

