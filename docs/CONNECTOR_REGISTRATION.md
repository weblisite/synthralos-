# Connector Registration Guide

## Problem
The platform has **99 connector manifest files** in `backend/app/connectors/manifests/`, but they haven't been registered in the database. This is why the Workflows tab shows "0 connectors" even though the manifest files exist.

## Solution
Run the connector registration script to register all 99 connectors into the database.

## Option 1: Run Locally (Recommended for Initial Setup)

```bash
cd backend
python scripts/register_connectors.py
```

This will:
- Register all 99 connectors from `app/connectors/manifests/`
- Mark them as platform connectors (available to all users)
- Create connector records and versions in the database

## Option 2: Run on Render (Via SSH/Console)

1. SSH into your Render backend service
2. Navigate to the backend directory
3. Run:
```bash
python scripts/register_connectors.py
```

## Option 3: Create an Admin Endpoint (For Future Use)

Add an admin endpoint to trigger connector registration:

```python
@router.post("/admin/connectors/init")
def init_all_connectors(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Initialize all connectors from manifest files (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin only")

    # Run registration script logic here
    ...
```

## Verification

After registration, verify connectors are in the database:

```sql
SELECT COUNT(*) FROM connector;
-- Should return 99

SELECT slug, name, status, is_platform FROM connector LIMIT 10;
```

## Files Involved

- **Manifest Files**: `backend/app/connectors/manifests/*.json` (99 files)
- **Registration Script**: `backend/scripts/register_connectors.py`
- **Registry Service**: `backend/app/connectors/registry.py`
- **Database Tables**: `connector`, `connectorversion`

## Notes

- Connectors are registered as **platform connectors** (`is_platform=True`)
- Each connector gets a version record in `connectorversion` table
- The registration script skips connectors that already exist
- All connectors are marked with status from manifest (draft, beta, stable)
