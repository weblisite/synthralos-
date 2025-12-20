"""
Initialize all connectors in the database.

This script registers all connector manifests from the manifests directory
into the database. It should be run once after database setup or migration.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.connectors.registry import (
    ConnectorNotFoundError,
    ConnectorRegistryError,
    InvalidManifestError,
    default_connector_registry,
)
from app.core.db import engine


def init_all_connectors():
    """Register all connector manifests."""
    manifests_dir = Path(__file__).parent.parent / "app" / "connectors" / "manifests"

    if not manifests_dir.exists():
        print(f"❌ Error: Manifests directory not found: {manifests_dir}")
        return False

    manifest_files = list(manifests_dir.glob("*.json"))
    print(f"📦 Found {len(manifest_files)} connector manifest(s)")

    if not manifest_files:
        print("⚠️  No manifest files found")
        return False

    registered_count = 0
    skipped_count = 0
    error_count = 0

    with Session(engine) as session:
        for manifest_file in sorted(manifest_files):
            slug = manifest_file.stem

            try:
                # Load manifest
                with open(manifest_file) as f:
                    manifest = json.load(f)

                name = manifest.get("name", slug)

                # Check if connector already exists
                try:
                    existing = default_connector_registry.get_connector(
                        session=session,
                        slug=slug,
                    )
                    skipped_count += 1
                    print(f"⏭️  Skipped {name} ({slug}) - already registered")
                    continue
                except ConnectorNotFoundError:
                    # Connector doesn't exist, proceed with registration
                    pass

                # Register connector as platform connector
                try:
                    connector_version = default_connector_registry.register_connector(
                        session=session,
                        manifest=manifest,
                        wheel_url=None,
                        owner_id=None,  # Platform connector
                        is_platform=True,
                        created_by=None,  # Platform connector
                    )

                    session.commit()
                    registered_count += 1
                    print(f"✅ Registered {name} ({slug}) v{connector_version.version}")

                except InvalidManifestError as e:
                    error_count += 1
                    print(f"❌ Invalid manifest for {name} ({slug}): {str(e)}")
                    session.rollback()
                except ConnectorRegistryError as e:
                    error_count += 1
                    print(f"❌ Error registering {name} ({slug}): {str(e)}")
                    session.rollback()

            except Exception as e:
                error_count += 1
                print(f"❌ Exception processing {slug}: {str(e)}")
                session.rollback()

    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  Total manifests: {len(manifest_files)}")
    print(f"  ✅ Registered: {registered_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"{'='*60}")

    return error_count == 0


if __name__ == "__main__":
    print("🚀 Initializing connectors...\n")
    success = init_all_connectors()
    if success:
        print("\n✅ Connector initialization completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Connector initialization completed with errors")
        sys.exit(1)
