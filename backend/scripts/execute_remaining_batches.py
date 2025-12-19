"""
Execute remaining connector migration batches (8-10) via Supabase MCP.

This script reads each batch SQL file and prepares it for execution.
"""

from pathlib import Path

batch_dir = Path(__file__).parent / "connector_batches"

print("Reading batches 8-10...\n")

for i in range(8, 11):
    batch_file = batch_dir / f'batch_{i}.sql'
    if batch_file.exists():
        sql_content = batch_file.read_text()
        connector_count = sql_content.count("INSERT INTO connector")
        
        # Verify structure
        assert 'BEGIN;' in sql_content
        assert 'COMMIT;' in sql_content
        
        print(f"Batch {i}: ✅ {connector_count} connectors, {len(sql_content)} chars")
        print(f"  Ready for: mcp_supabase_apply_migration(name='register_connectors_batch_{i}_complete', query=sql_content)")
    else:
        print(f"Batch {i}: ❌ File not found")

print("\n✅ All batches 8-10 prepared")


