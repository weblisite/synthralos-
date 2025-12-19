"""
Execute all connector migration batches via Supabase MCP.

This script reads each batch SQL file and prepares it for execution.
The actual execution should be done via Supabase MCP execute_sql or apply_migration.
"""

from pathlib import Path
import json

batch_dir = Path(__file__).parent / "connector_batches"
batches = sorted([f for f in batch_dir.glob('batch_*.sql')], key=lambda x: int(x.stem.split('_')[1]))

print(f"Found {len(batches)} batch files\n")

batch_data = []

for i, batch_file in enumerate(batches, 1):
    sql_content = batch_file.read_text()
    connector_count = sql_content.count("INSERT INTO connector")
    
    batch_info = {
        'batch_num': i,
        'file': batch_file.name,
        'sql': sql_content,
        'size': len(sql_content),
        'connector_count': connector_count
    }
    
    batch_data.append(batch_info)
    
    print(f"Batch {i}: {connector_count} connectors, {len(sql_content)} chars")

# Save all batches to JSON
output_file = Path(__file__).parent.parent / 'connector_batches_complete.json'
with open(output_file, 'w') as f:
    json.dump({
        'total_batches': len(batches),
        'total_connectors': sum(b['connector_count'] for b in batch_data),
        'batches': batch_data
    }, f, indent=2)

print(f"\n✅ All batches prepared")
print(f"📁 Saved to: {output_file}")
print(f"📊 Total connectors: {sum(b['connector_count'] for b in batch_data)}")
print(f"\nTo execute:")
print(f"  For each batch, use: mcp_supabase_execute_sql(query=batch['sql'])")
print(f"  Or: mcp_supabase_apply_migration(name='batch_{i}', query=batch['sql'])")


