"""
Execute connector migration by reading manifest files and inserting directly.

This script reads all connector manifests and inserts them one by one,
handling conflicts properly.
"""

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.connectors.registry import default_connector_registry
from app.core.db import engine

MANIFESTS_DIR = Path(__file__).parent.parent / "app" / "connectors" / "manifests"


def migrate_all_connectors():
    """Migrate all connectors from manifest files."""
    manifest_files = sorted(MANIFESTS_DIR.glob("*.json"))
    
    if not manifest_files:
        print("❌ No manifest files found")
        return False
    
    print(f"📦 Found {len(manifest_files)} connector manifest(s)\n")
    
    success_count = 0
    error_count = 0
    
    with Session(engine) as session:
        for manifest_file in manifest_files:
            try:
                with open(manifest_file, "r") as f:
                    manifest = json.load(f)
                
                slug = manifest.get("slug")
                name = manifest.get("name")
                
                if not slug or not name:
                    print(f"⚠️  Skipping {manifest_file.name}: missing slug or name")
                    continue
                
                # Check if connector already exists
                existing = session.exec(
                    select(default_connector_registry.Connector).where(
                        default_connector_registry.Connector.slug == slug,
                        default_connector_registry.Connector.is_platform == True,
                    )
                ).first()
                
                if existing:
                    print(f"⏭️  Skipping {name} ({slug}): already exists")
                    continue
                
                # Register connector using the registry
                connector_version = default_connector_registry.register_connector(
                    session=session,
                    manifest=manifest,
                    is_platform=True,
                )
                
                session.commit()
                success_count += 1
                print(f"✅ Registered: {name} ({slug}) v{manifest.get('version', '1.0.0')}")
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error processing {manifest_file.name}: {str(e)}")
                session.rollback()
                continue
    
    print(f"\n✅ Migration complete!")
    print(f"   Success: {success_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total: {len(manifest_files)}")
    
    return success_count > 0


if __name__ == "__main__":
    print("🚀 Starting connector migration...\n")
    success = migrate_all_connectors()
    sys.exit(0 if success else 1)


