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

# Start the backend server using uvicorn
# Render provides PORT environment variable automatically (defaults to 10000)
# Use 0.0.0.0 to bind to all interfaces (required for Render)
# Don't hardcode a fallback - use Render's default if somehow not set
if [ -z "$PORT" ]; then
    echo "⚠️  PORT environment variable not set. Render should provide this automatically."
    echo "Using Render's default port 10000"
    PORT=10000
else
    echo "✅ Using PORT from Render: $PORT"
fi
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

# Skip import test - it can hang due to heavy imports/memory issues
# Uvicorn will handle imports and show errors if any
# This prevents the startup script from hanging indefinitely
echo "Skipping import test (uvicorn will handle imports and show errors if any)"
echo "Starting uvicorn directly..."

# Use python -m uvicorn for better reliability
# Add --log-level info for better debugging
# Use --timeout-keep-alive to prevent connection issues
# Use --access-log to see all requests
echo "Executing: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info --timeout-keep-alive 30 --access-log"
echo "Server should be accessible at http://0.0.0.0:$PORT"
echo "Health check: http://0.0.0.0:$PORT/api/v1/utils/health-check"

# Use python -m uvicorn explicitly (more reliable than direct uvicorn command)
# Add error handling and ensure we see what's happening
# Use --no-access-log initially to reduce memory usage, can enable later if needed
echo ""
echo "🚀 Starting uvicorn server..."
echo "This may take a moment due to heavy imports..."

# Run uvicorn (removed --access-log to reduce memory usage)
# Removed tee/logging as it may cause issues in Render environment
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info \
    --timeout-keep-alive 30 \
    --no-server-header || {
    EXIT_CODE=$?
    echo ""
    echo "❌ Uvicorn failed to start. Exit code: $EXIT_CODE"
    echo "This may be due to memory constraints (starter plan has 512MB limit)"
    echo "Consider upgrading to Standard plan (2GB) for better reliability"
    exit $EXIT_CODE
}
