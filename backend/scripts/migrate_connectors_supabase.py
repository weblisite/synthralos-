"""
Migrate all connector manifests to Supabase database using Supabase MCP.

This script reads all connector manifest JSON files and registers them
in the Supabase database as platform connectors.
"""

import json
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# This script will be run manually with Supabase MCP access
# It generates SQL INSERT statements that can be executed via Supabase MCP

MANIFESTS_DIR = Path(__file__).parent.parent / "app" / "connectors" / "manifests"


def generate_connector_sql():
    """Generate SQL INSERT statements for all connectors."""
    manifest_files = sorted(MANIFESTS_DIR.glob("*.json"))
    
    if not manifest_files:
        print("❌ No manifest files found")
        return None
    
    print(f"📦 Found {len(manifest_files)} connector manifest(s)\n")
    
    connector_inserts = []
    version_inserts = []
    connector_updates = []
    
    for manifest_file in manifest_files:
        try:
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
            
            slug = manifest.get("slug")
            name = manifest.get("name")
            version_str = manifest.get("version", "1.0.0")
            status = manifest.get("status", "draft")
            
            if not slug or not name:
                print(f"⚠️  Skipping {manifest_file.name}: missing slug or name")
                continue
            
            # Generate UUIDs
            connector_id = str(uuid.uuid4())
            version_id = str(uuid.uuid4())
            
            # Escape JSON for SQL
            manifest_json = json.dumps(manifest).replace("'", "''")
            created_at = datetime.utcnow().isoformat()
            
            # INSERT connector
            connector_sql = f"""
INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '{connector_id}',
    '{slug}',
    '{name.replace("'", "''")}',
    '{status}',
    '{version_id}',
    '{created_at}',
    NULL,
    true,
    NULL
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    latest_version_id = EXCLUDED.latest_version_id,
    is_platform = true,
    owner_id = NULL,
    created_by = NULL;
"""
            
            # INSERT connector version
            version_sql = f"""
INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
VALUES (
    '{version_id}',
    '{connector_id}',
    '{version_str}',
    '{manifest_json}'::jsonb,
    NULL,
    '{created_at}'
)
ON CONFLICT DO NOTHING;
"""
            
            connector_inserts.append(connector_sql)
            version_inserts.append(version_sql)
            
            print(f"✅ Prepared: {name} ({slug}) v{version_str}")
            
        except Exception as e:
            print(f"❌ Error processing {manifest_file.name}: {str(e)}")
            continue
    
    # Combine all SQL statements
    full_sql = """
-- Migrate all connectors to Supabase
-- Generated: """ + datetime.utcnow().isoformat() + """
-- Total connectors: """ + str(len(connector_inserts)) + """

BEGIN;

""" + "\n".join(connector_inserts) + "\n" + "\n".join(version_inserts) + """

COMMIT;

-- Verify migration
SELECT COUNT(*) as total_connectors FROM connector;
SELECT COUNT(*) as total_versions FROM connectorversion;
"""
    
    return full_sql


if __name__ == "__main__":
    print("🚀 Generating connector migration SQL...\n")
    sql = generate_connector_sql()
    
    if sql:
        # Write to file
        output_file = Path(__file__).parent / "migrate_connectors.sql"
        with open(output_file, "w") as f:
            f.write(sql)
        
        print(f"\n✅ SQL migration file generated: {output_file}")
        print(f"📝 Total connectors prepared: {len([s for s in sql.split('INSERT INTO connector') if 'VALUES' in s])}")
        print("\nTo apply this migration, use Supabase MCP:")
        print("  mcp_supabase_apply_migration(name='register_all_connectors', query=<sql_content>)")
    else:
        print("\n❌ Failed to generate migration SQL")
        sys.exit(1)


