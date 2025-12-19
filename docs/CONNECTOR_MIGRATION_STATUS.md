# Connector Migration Status

## Summary
Migrated 99 connectors from manifest files to Supabase database using Supabase MCP.

## Migration Process

1. **Created Migration Scripts**:
   - `backend/scripts/migrate_connectors_supabase.py` - Generates SQL from manifests
   - `backend/scripts/migrate_connectors_batch.py` - Generates batched SQL (10 batches of ~10 connectors each)
   - `backend/scripts/connector_batches/batch_1.sql` through `batch_10.sql` - Individual batch SQL files

2. **Migration Method**:
   - Used Supabase MCP `apply_migration` to execute batches
   - Each batch contains INSERT statements for connectors and connector versions
   - Used `ON CONFLICT` clauses to handle existing connectors gracefully
   - Used SELECT subqueries to resolve foreign key relationships

3. **Status**:
   - ✅ Batch 1 executed successfully (10 connectors)
   - ⏳ Batches 2-10 pending execution

## To Complete Migration

Execute remaining batches via Supabase MCP:

```bash
# Execute batches 2-10
for i in {2..10}; do
  mcp_supabase_apply_migration(
    name=f"register_connectors_batch_{i}",
    query=<read batch_${i}.sql content>
  )
done
```

Or execute all batches via SQL:

```sql
-- Read and execute each batch file from:
-- backend/scripts/connector_batches/batch_2.sql through batch_10.sql
```

## Verification

After migration, verify:

```sql
SELECT COUNT(*) FROM connector WHERE is_platform = true;
-- Should return 99

SELECT COUNT(*) FROM connectorversion;
-- Should return 99

SELECT slug, name, status FROM connector WHERE is_platform = true ORDER BY slug;
-- Should list all 99 connectors
```

## Files

- **Manifest Files**: `backend/app/connectors/manifests/*.json` (99 files)
- **Batch SQL Files**: `backend/scripts/connector_batches/batch_*.sql` (10 files)
- **Migration Scripts**: `backend/scripts/migrate_connectors_*.py`

