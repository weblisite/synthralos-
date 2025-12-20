"""
Migrate connectors in batches using Supabase MCP.

This script reads connector manifests and generates batch SQL statements
that can be executed via Supabase MCP execute_sql.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

MANIFESTS_DIR = Path(__file__).parent.parent / "app" / "connectors" / "manifests"
BATCH_SIZE = 10  # Process 10 connectors at a time


def generate_batch_sql(manifest_files, batch_num, total_batches):
    """Generate SQL for a batch of connectors."""
    sql_parts = []

    for manifest_file in manifest_files:
        try:
            with open(manifest_file) as f:
                manifest = json.load(f)

            slug = manifest.get("slug")
            name = manifest.get("name")
            version_str = manifest.get("version", "1.0.0")
            status = manifest.get("status", "draft")

            if not slug or not name:
                continue

            # Generate UUIDs
            connector_id = str(uuid.uuid4())
            version_id = str(uuid.uuid4())

            # Escape JSON and strings for SQL
            manifest_json = json.dumps(manifest).replace("'", "''")
            name_escaped = name.replace("'", "''")
            created_at = datetime.now(timezone.utc).isoformat()

            # INSERT connector
            connector_sql = f"""INSERT INTO connector (id, slug, name, status, latest_version_id, created_at, owner_id, is_platform, created_by)
VALUES (
    '{connector_id}',
    '{slug}',
    '{name_escaped}',
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
    created_by = NULL;"""

            # INSERT connector version - use subquery to get connector_id from slug
            version_sql = f"""INSERT INTO connectorversion (id, connector_id, version, manifest, wheel_url, created_at)
SELECT
    '{version_id}',
    c.id,
    '{version_str}',
    '{manifest_json}'::jsonb,
    NULL,
    '{created_at}'
FROM connector c
WHERE c.slug = '{slug}' AND c.is_platform = true
ON CONFLICT DO NOTHING;"""

            sql_parts.append(connector_sql)
            sql_parts.append(version_sql)

        except Exception as e:
            print(f"Error processing {manifest_file.name}: {e}")
            continue

    full_sql = (
        f"""
-- Batch {batch_num} of {total_batches}
-- Migrating {len(manifest_files)} connectors

BEGIN;

"""
        + "\n\n".join(sql_parts)
        + """

COMMIT;

-- Verify this batch
SELECT COUNT(*) as connectors_after_batch FROM connector;
"""
    )

    return full_sql


def main():
    """Generate batch SQL files."""
    manifest_files = sorted(MANIFESTS_DIR.glob("*.json"))
    total_files = len(manifest_files)
    total_batches = (total_files + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"📦 Found {total_files} connector manifest(s)")
    print(f"📊 Will process in {total_batches} batch(es) of {BATCH_SIZE}\n")

    batches = []
    for i in range(0, total_files, BATCH_SIZE):
        batch_files = manifest_files[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        sql = generate_batch_sql(batch_files, batch_num, total_batches)
        batches.append(sql)
        print(
            f"✅ Generated batch {batch_num}/{total_batches} ({len(batch_files)} connectors)"
        )

    # Save all batches
    output_dir = Path(__file__).parent / "connector_batches"
    output_dir.mkdir(exist_ok=True)

    for i, sql in enumerate(batches, 1):
        output_file = output_dir / f"batch_{i}.sql"
        output_file.write_text(sql)
        print(f"💾 Saved {output_file}")

    print(f"\n✅ Generated {len(batches)} batch SQL file(s)")
    print(f"📁 Location: {output_dir}")
    print("\nTo apply via Supabase MCP, execute each batch SQL file using:")
    print("  mcp_supabase_execute_sql(query=<batch_sql_content>)")

    return batches


if __name__ == "__main__":
    main()
