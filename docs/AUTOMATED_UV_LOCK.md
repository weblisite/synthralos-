# Automated uv.lock Management

This document explains how we automatically keep `uv.lock` in sync with `pyproject.toml`.

## Problem

When packages are added to `pyproject.toml`, the `uv.lock` file must be updated by running `uv lock`. If this is forgotten:
- Docker builds fail (they use `uv sync --frozen` which reads `uv.lock` only)
- Packages won't be installed in production
- Builds become non-reproducible

## Solution: Automated Checks

We've implemented **two layers** of automation:

### 1. Pre-commit Hook (Local)

**Location**: `.pre-commit-config.yaml` → `check-uv-lock` hook
**Script**: `backend/scripts/check-uv-lock.sh`

**What it does**:
- Detects when `pyproject.toml` is modified or staged
- Automatically runs `uv lock` to update `uv.lock`
- Auto-stages the updated `uv.lock` file
- Blocks commit if `uv` is not available

**How to use**:
```bash
# Install pre-commit hooks (one-time setup)
cd backend
uv run pre-commit install

# Now when you commit:
git add backend/pyproject.toml
git commit -m "Add new package"
# ✅ Pre-commit hook automatically updates and stages uv.lock
```

**Example output**:
```
📦 pyproject.toml changed detected
🔍 Checking if uv.lock needs updating...
⚠️  uv.lock is out of sync with pyproject.toml
🔄 Running 'uv lock' to update uv.lock...
✅ uv.lock has been updated
📝 Auto-staged updated uv.lock
```

### 2. GitHub Actions (CI)

**Location**: `.github/workflows/ci.yml` → `check-uv-lock` job

**What it does**:
- Runs on every push and pull request
- Verifies `uv.lock` is in sync with `pyproject.toml`
- Fails the CI build if they're out of sync

**How it works**:
```yaml
- name: Check uv.lock is in sync
  working-directory: ./backend
  run: uv lock --check
```

If `uv.lock` is out of sync, the CI will fail with:
```
Error: uv.lock is out of sync with pyproject.toml
```

## Workflow

### Adding a New Package

1. **Edit `pyproject.toml`**:
   ```toml
   dependencies = [
       # ... existing packages ...
       "new-package>=1.0.0",
   ]
   ```

2. **Stage the change**:
   ```bash
   git add backend/pyproject.toml
   ```

3. **Commit**:
   ```bash
   git commit -m "Add new-package"
   ```

4. **Pre-commit hook automatically**:
   - Detects `pyproject.toml` changed
   - Runs `uv lock`
   - Stages `uv.lock`
   - Allows commit to proceed

5. **Both files are committed together**:
   ```bash
   git log --oneline -1
   # Shows: "Add new-package"

   git show --name-only HEAD
   # Shows: backend/pyproject.toml, backend/uv.lock
   ```

### Manual Update (if needed)

If you need to manually update `uv.lock`:

```bash
cd backend
uv lock
git add uv.lock
git commit -m "Update uv.lock"
```

## Troubleshooting

### Pre-commit hook not running?

```bash
# Reinstall pre-commit hooks
cd backend
uv run pre-commit install

# Test manually
uv run pre-commit run check-uv-lock --all-files
```

### uv not found?

Install `uv`:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### CI failing?

If CI fails with "uv.lock is out of sync":
1. Run `uv lock` locally
2. Commit the updated `uv.lock`
3. Push again

## Benefits

✅ **Prevents missing packages** - Catches issues before they reach production
✅ **Automatic** - No manual steps required
✅ **Fast feedback** - Pre-commit hook runs instantly
✅ **CI safety net** - GitHub Actions catches if hook is bypassed
✅ **Reproducible builds** - Ensures `uv.lock` is always in sync

## Related Documentation

- [UV Lock Explanation](./UV_LOCK_EXPLANATION.md) - How `pyproject.toml` and `uv.lock` work together
- [Development Guide](../development.md) - General development workflow
