#!/bin/bash
# Pre-commit hook to ensure uv.lock is in sync with pyproject.toml
# This script automatically updates uv.lock when pyproject.toml changes

set -e

cd "$(dirname "$0")/.." || exit 1

# Check if pyproject.toml is staged or modified
if git diff --cached --name-only | grep -q "pyproject.toml" || \
   git diff --name-only | grep -q "pyproject.toml"; then
    echo "📦 pyproject.toml changed detected"
    
    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        echo "⚠️  uv not found in PATH. Install it from https://docs.astral.sh/uv/"
        echo "   Skipping uv.lock update check."
        exit 0
    fi
    
    # Check if uv.lock needs updating
    echo "🔍 Checking if uv.lock needs updating..."
    
    # Save current state
    LOCK_FILE="uv.lock"
    LOCK_WAS_STAGED=false
    
    if git diff --cached --name-only | grep -q "$LOCK_FILE"; then
        LOCK_WAS_STAGED=true
    fi
    
    # Run uv lock to update lock file
    if uv lock --check 2>/dev/null; then
        echo "✅ uv.lock is already in sync with pyproject.toml"
    else
        echo "⚠️  uv.lock is out of sync with pyproject.toml"
        echo "🔄 Running 'uv lock' to update uv.lock..."
        uv lock
        
        # Check if uv.lock changed
        if git diff --name-only | grep -q "$LOCK_FILE" || \
           git diff --cached --name-only | grep -q "$LOCK_FILE"; then
            echo "✅ uv.lock has been updated"
            
            # Auto-stage the updated lock file
            git add "$LOCK_FILE"
            echo "📝 Auto-staged updated uv.lock"
            
            if [ "$LOCK_WAS_STAGED" = false ]; then
                echo ""
                echo "ℹ️  uv.lock has been automatically updated and staged."
                echo "   You can now commit both pyproject.toml and uv.lock together."
            fi
        else
            echo "✅ uv.lock is now in sync"
        fi
    fi
fi

exit 0

