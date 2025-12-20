# Setting Up Pre-commit Hooks

This guide explains how to install and set up pre-commit hooks for automated `uv.lock` management.

## Prerequisites

- Python 3.10+ installed
- `uv` package manager installed ([Installation guide](https://docs.astral.sh/uv/))

## Installation Methods

### Method 1: Using uv (Recommended)

Since `pre-commit` is already in `backend/pyproject.toml` dev-dependencies:

```bash
cd backend
uv sync
uv run pre-commit install
```

### Method 2: Using pip

```bash
pip install pre-commit
pre-commit install
```

### Method 3: Using Homebrew (macOS)

```bash
brew install pre-commit
pre-commit install
```

## Verify Installation

After installation, verify the hooks are installed:

```bash
# Check if hooks are installed
ls -la .git/hooks/pre-commit

# Test the hook manually
pre-commit run check-uv-lock --all-files
```

## Testing the Automation

### Test 1: Make a change to pyproject.toml

1. **Add a test comment** (or add a package):
   ```bash
   # Edit backend/pyproject.toml
   # Add a comment or add a test package
   ```

2. **Stage the change**:
   ```bash
   git add backend/pyproject.toml
   ```

3. **Try to commit**:
   ```bash
   git commit -m "Test: verify uv.lock automation"
   ```

4. **Expected behavior**:
   - Pre-commit hook runs automatically
   - If `pyproject.toml` changed, it runs `uv lock`
   - Auto-stages `uv.lock` if it was updated
   - Commit proceeds with both files

### Test 2: Manual hook execution

```bash
# Run the hook manually
pre-commit run check-uv-lock --all-files

# Or run all hooks
pre-commit run --all-files
```

## Troubleshooting

### Hook not running?

1. **Verify installation**:
   ```bash
   ls -la .git/hooks/pre-commit
   ```

2. **Reinstall**:
   ```bash
   pre-commit uninstall
   pre-commit install
   ```

### uv not found?

Install `uv`:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### Hook fails with platform error?

If you see errors about `onnxruntime` or platform compatibility:
- This is a known issue with some dependencies
- The hook will still work for `uv.lock` updates
- You can skip the problematic dependencies or use Docker for development

### Bypass hooks (not recommended)

If you need to bypass hooks temporarily:
```bash
git commit --no-verify -m "Emergency commit"
```

**Note**: CI will still check `uv.lock` sync, so this should only be used in emergencies.

## What Happens When You Commit

1. **Pre-commit hook runs** (`check-uv-lock`)
2. **Checks if `pyproject.toml` changed**
3. **If changed**:
   - Runs `uv lock` to update `uv.lock`
   - Auto-stages `uv.lock`
   - Shows status messages
4. **Commit proceeds** with both files staged

## Example Output

When you commit with `pyproject.toml` changes:

```
📦 pyproject.toml changed detected
🔍 Checking if uv.lock needs updating...
⚠️  uv.lock is out of sync with pyproject.toml
🔄 Running 'uv lock' to update uv.lock...
✅ uv.lock has been updated
📝 Auto-staged updated uv.lock
```

## Related Documentation

- [Automated uv.lock Management](./AUTOMATED_UV_LOCK.md) - How the automation works
- [UV Lock Explanation](./UV_LOCK_EXPLANATION.md) - Understanding pyproject.toml vs uv.lock
- [Development Guide](../development.md) - General development workflow

