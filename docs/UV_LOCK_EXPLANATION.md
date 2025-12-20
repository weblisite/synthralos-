# Understanding `pyproject.toml` vs `uv.lock`

## Overview

`uv` (the Python package manager) uses a two-file system similar to npm (`package.json` + `package-lock.json`) or Rust (`Cargo.toml` + `Cargo.lock`):

- **`pyproject.toml`** = Source of truth (what you want)
- **`uv.lock`** = Locked/resolved versions (exact versions installed)

## How They Work Together

### 1. `pyproject.toml` (Source of Truth)
- **Purpose**: Declares your direct dependencies with version ranges
- **Example**: `"nango>=0.1.0"` means "I want nango version 0.1.0 or higher"
- **Contains**: Only packages you directly depend on
- **Human-editable**: Yes, you manually add/remove packages here

### 2. `uv.lock` (Locked Versions)
- **Purpose**: Contains exact versions of ALL packages (direct + transitive dependencies)
- **Example**: `nango = "0.1.2"` (exact version)
- **Contains**: Every package needed, including dependencies of dependencies
- **Auto-generated**: Created/updated by `uv lock` or `uv sync`

## Commands and Their Behavior

### `uv lock`
- **Reads**: `pyproject.toml`
- **Updates**: `uv.lock` (resolves all dependencies to exact versions)
- **Installs**: Nothing
- **Use case**: Update lock file after changing `pyproject.toml`

### `uv sync`
- **Reads**: `pyproject.toml`
- **Updates**: `uv.lock` (if needed)
- **Installs**: All packages from resolved dependencies
- **Use case**: Development - installs and keeps lock file in sync

### `uv sync --frozen`
- **Reads**: `uv.lock` ONLY (ignores `pyproject.toml`)
- **Updates**: Nothing
- **Installs**: Exact versions from `uv.lock`
- **Use case**: Production/Docker builds - ensures reproducible installs

## Why This Matters

### The Problem We Had
1. ✅ Nango was added to `pyproject.toml` (`"nango>=0.1.0"`)
2. ❌ `uv.lock` was NOT updated (didn't run `uv lock`)
3. ❌ Dockerfile uses `uv sync --frozen` (reads `uv.lock` only)
4. ❌ Result: Nango was NOT installed because it wasn't in `uv.lock`

### The Solution
1. ✅ Ran `uv lock` to regenerate `uv.lock`
2. ✅ `uv.lock` now contains `nango = "0.1.2"`
3. ✅ Docker build will now install Nango

## Best Practices

### ✅ DO:
- **Always run `uv lock`** after adding/removing packages in `pyproject.toml`
- **Commit `uv.lock`** to version control (ensures reproducible builds)
- **Use `uv sync --frozen`** in production/Docker (ensures exact versions)

### ❌ DON'T:
- **Don't manually edit `uv.lock`** (it's auto-generated)
- **Don't forget to run `uv lock`** after changing `pyproject.toml`
- **Don't use `uv sync` in production** (use `--frozen` for reproducibility)

## Workflow Example

```bash
# 1. Add a new package to pyproject.toml
# Edit: dependencies = [..., "new-package>=1.0.0"]

# 2. Update the lock file
uv lock

# 3. Install packages (development)
uv sync

# 4. In Dockerfile (production)
uv sync --frozen  # Uses uv.lock only
```

## Current Dockerfile Pattern

Looking at `backend/Dockerfile`:

```dockerfile
# Step 1: Install dependencies from lock file (frozen = exact versions)
RUN uv sync --frozen --no-install-project

# Step 2: Copy project files
COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/
COPY ./app /app/app

# Step 3: Sync project (reads pyproject.toml, but lock file already exists)
RUN uv sync
```

**Note**: Step 3 (`uv sync`) will use the existing `uv.lock` if it matches `pyproject.toml`. If they don't match, it will update `uv.lock` and reinstall.

## Summary

- **`pyproject.toml`**: What you want (version ranges)
- **`uv.lock`**: Exact versions that will be installed
- **Always keep them in sync**: Run `uv lock` after changing `pyproject.toml`
- **Production uses `uv.lock`**: `uv sync --frozen` ensures reproducible builds

