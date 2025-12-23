#!/bin/bash
# Development Workflow Worker Startup Script
#
# This script starts the workflow worker for local development.
# Run this in a separate terminal from the backend server.

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to backend directory
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e ."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if database is configured
if [ -z "$SUPABASE_DB_URL" ] && [ -z "$SUPABASE_URL" ] && [ -z "$POSTGRES_HOST" ]; then
    echo "⚠️  Warning: Database environment variables not set."
    echo "   The worker needs database access to function."
    echo "   Set SUPABASE_DB_URL or SUPABASE_URL + SUPABASE_DB_PASSWORD"
    echo ""
fi

# Start the worker
echo "============================================================"
echo "🚀 Starting Workflow Worker (Development)"
echo "============================================================"
echo ""
echo "The worker will:"
echo "  • Poll database every 1 second for workflow executions"
echo "  • Process running executions"
echo "  • Handle retries, signals, and scheduled executions"
echo "  • Execute workflow nodes via activity handlers"
echo ""
echo "Press Ctrl+C to stop the worker"
echo "============================================================"
echo ""

python -m scripts.start_worker
