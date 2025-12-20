# Connector Database Schema Explanation

## Overview

**All connectors are stored in ONE shared table** (`connector`), not separate tables for each connector. This is a **normalized relational database design** where:

- **One table** stores connector metadata (name, slug, status, etc.)
- **One table** stores connector versions (manifests, versions, etc.)
- All 99 connectors share the same table structure

## Database Structure

### Table 1: `connector` (Main Connector Table)

This is the **single table** that stores ALL connectors. Each connector gets **one row** in this table.

**Columns:**
- `id` (UUID) - Primary key, unique identifier for each connector
- `slug` (VARCHAR) - Unique identifier like "gmail", "stripe", "github" (UNIQUE constraint)
- `name` (VARCHAR) - Display name like "Gmail", "Stripe", "GitHub"
- `status` (VARCHAR) - Status: "draft", "beta", "stable", or "deprecated"
- `latest_version_id` (UUID) - Foreign key to the latest version in `connectorversion` table
- `created_at` (TIMESTAMP) - When the connector was created
- `owner_id` (UUID, nullable) - Foreign key to `user` table (NULL for platform connectors)
- `is_platform` (BOOLEAN) - `true` for platform connectors (available to all users), `false` for user-specific connectors
- `created_by` (UUID, nullable) - Foreign key to `user` table (who created it)

**Example Data:**
```
id: 731167b1-7ed6-4d38-9e13-5a26d220104f
slug: "gmail"
name: "Gmail"
status: "beta"
latest_version_id: 0fe9423a-82d6-4af8-9978-7046b28c300e
is_platform: true
owner_id: NULL
```

### Table 2: `connectorversion` (Connector Versions Table)

This table stores **versions** of connectors. Each connector can have multiple versions over time.

**Columns:**
- `id` (UUID) - Primary key, unique identifier for each version
- `connector_id` (UUID) - Foreign key to `connector.id` (which connector this version belongs to)
- `version` (VARCHAR) - Version string like "1.0.0", "1.1.0", etc.
- `manifest` (JSONB) - The full connector manifest JSON (actions, triggers, OAuth config, etc.)
- `wheel_url` (VARCHAR, nullable) - URL to Python wheel file if applicable
- `created_at` (TIMESTAMP) - When this version was created

**Example Data:**
```
id: 0fe9423a-82d6-4af8-9978-7046b28c300e
connector_id: 731167b1-7ed6-4d38-9e13-5a26d220104f (references Gmail connector)
version: "1.0.0"
manifest: {
  "name": "Gmail",
  "slug": "gmail",
  "version": "1.0.0",
  "description": "Send and receive emails via Gmail API",
  "category": "Communication & Collaboration",
  "status": "beta",
  "nango": {...},
  "oauth": {...},
  "actions": {...},
  "triggers": {...}
}
```

## Relationship Between Tables

```
connector (1) ──< (many) connectorversion
```

- **One connector** can have **many versions**
- Each version references exactly **one connector** via `connector_id`
- The `connector.latest_version_id` points to the most recent version

## How It Works

### When a Connector is Created:

1. **Insert into `connector` table:**
   ```sql
   INSERT INTO connector (id, slug, name, status, is_platform, ...)
   VALUES ('uuid', 'gmail', 'Gmail', 'beta', true, ...);
   ```

2. **Insert into `connectorversion` table:**
   ```sql
   INSERT INTO connectorversion (id, connector_id, version, manifest, ...)
   VALUES ('uuid', 'connector-uuid', '1.0.0', '{...manifest...}', ...);
   ```

3. **Update connector with latest version:**
   ```sql
   UPDATE connector
   SET latest_version_id = 'version-uuid'
   WHERE id = 'connector-uuid';
   ```

### When Querying Connectors:

```sql
-- Get all connectors with their latest version
SELECT
    c.id,
    c.slug,
    c.name,
    c.status,
    cv.version,
    cv.manifest
FROM connector c
LEFT JOIN connectorversion cv ON c.latest_version_id = cv.id
WHERE c.is_platform = true;
```

## Why This Design?

### ✅ Advantages:

1. **Normalized Structure**: All connectors share the same schema, making queries consistent
2. **Versioning Support**: Easy to track multiple versions of the same connector
3. **Efficient Queries**: Can query all connectors with a single SQL statement
4. **Flexible**: Easy to add new connectors without schema changes
5. **Scalable**: Can handle thousands of connectors efficiently

### ❌ Alternative (Not Used):

**Separate table per connector** would be:
- ❌ Inefficient (99+ tables to manage)
- ❌ Hard to query (need UNION queries)
- ❌ Schema changes require updating all tables
- ❌ No versioning support built-in

## Current Status

- **Total Connectors**: 99 manifest files
- **Database Records**:
  - `connector` table: 1 row (ActiveCampaign - batch 1 executed)
  - `connectorversion` table: 2 rows (versions for ActiveCampaign)
- **Remaining**: 98 connectors pending migration (batches 2-10)

## Example: All 99 Connectors in One Table

After migration completes, the `connector` table will look like:

```
| id                                  | slug              | name              | status | is_platform |
|-------------------------------------|-------------------|-------------------|--------|-------------|
| uuid-1                              | gmail             | Gmail             | beta   | true        |
| uuid-2                              | stripe            | Stripe            | beta   | true        |
| uuid-3                              | github            | GitHub            | beta   | true        |
| uuid-4                              | slack             | Slack             | beta   | true        |
| ...                                 | ...               | ...               | ...    | ...         |
| uuid-99                             | zoom              | Zoom              | beta   | true        |
```

All 99 connectors in **one table**, each with their own row!

## Summary

- ✅ **One table** (`connector`) stores ALL connectors
- ✅ **One table** (`connectorversion`) stores ALL connector versions
- ✅ Each connector = **one row** in `connector` table
- ✅ Each version = **one row** in `connectorversion` table
- ✅ All 99 connectors share the same table structure
- ✅ No separate tables per connector

This is a **standard relational database design** pattern called **normalization** - storing similar entities in the same table rather than creating separate tables for each entity.
