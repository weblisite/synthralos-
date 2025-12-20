"""
Script to register all connector manifests via the API or directly.

Can be run in two modes:
1. Direct mode: Registers directly using the ConnectorRegistry (no auth needed)
2. API mode: Registers via HTTP API (requires authentication token)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.connectors.registry import (
    ConnectorRegistryError,
    InvalidManifestError,
    default_connector_registry,
)
from app.core.db import engine


def register_connector_direct(
    session: Session,
    manifest_path: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Register a connector directly using the ConnectorRegistry.

    Args:
        session: Database session
        manifest_path: Path to manifest JSON file
        dry_run: If True, validate but don't register

    Returns:
        Registration result dictionary
    """
    # Load manifest
    with open(manifest_path) as f:
        manifest = json.load(f)

    if dry_run:
        # Just validate
        registry = default_connector_registry
        registry.validate_manifest(manifest)
        return {
            "status": "validated",
            "slug": manifest.get("slug"),
            "name": manifest.get("name"),
        }

    # Register
    registry = default_connector_registry

    try:
        connector_version = registry.register_connector(
            session=session,
            manifest=manifest,
            wheel_url=None,
        )

        return {
            "status": "registered",
            "id": str(connector_version.id),
            "connector_id": str(connector_version.connector_id),
            "slug": manifest.get("slug"),
            "name": manifest.get("name"),
            "version": connector_version.version,
        }
    except InvalidManifestError as e:
        return {
            "status": "error",
            "slug": manifest.get("slug"),
            "name": manifest.get("name"),
            "error": f"Invalid manifest: {str(e)}",
        }
    except ConnectorRegistryError as e:
        return {
            "status": "error",
            "slug": manifest.get("slug"),
            "name": manifest.get("name"),
            "error": str(e),
        }


def register_all_connectors(
    manifests_dir: Path,
    dry_run: bool = False,
    connector_slug: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    """
    Register all connectors from manifest files.

    Args:
        manifests_dir: Directory containing manifest JSON files
        dry_run: If True, validate but don't register
        connector_slug: Optional single connector slug to register
        category: Optional category filter

    Returns:
        Summary dictionary with registration results
    """
    # Get all manifest files
    manifest_files = list(manifests_dir.glob("*.json"))

    if connector_slug:
        # Filter to specific connector
        manifest_files = [f for f in manifest_files if f.stem == connector_slug]
        if not manifest_files:
            return {
                "error": f"Connector '{connector_slug}' not found in manifests directory",
            }

    # Filter by category if specified
    if category:
        filtered_files = []
        for manifest_file in manifest_files:
            with open(manifest_file) as f:
                manifest = json.load(f)
                if manifest.get("category") == category:
                    filtered_files.append(manifest_file)
        manifest_files = filtered_files

    if not manifest_files:
        return {
            "error": "No manifest files found matching criteria",
        }

    print(
        f"{'Validating' if dry_run else 'Registering'} {len(manifest_files)} connector(s)...\n"
    )

    results = {
        "registered": [],
        "skipped": [],
        "errors": [],
        "total": len(manifest_files),
    }

    # Use database session
    with Session(engine) as session:
        for manifest_file in sorted(manifest_files):
            slug = manifest_file.stem

            try:
                # Load manifest to get name
                with open(manifest_file) as f:
                    manifest = json.load(f)
                    name = manifest.get("name", slug)

                # Check if connector already exists
                if not dry_run:
                    try:
                        existing = default_connector_registry.get_connector(
                            session=session,
                            slug=slug,
                        )
                        results["skipped"].append(
                            {
                                "slug": slug,
                                "name": name,
                                "reason": f"Already registered (version {existing.version})",
                            }
                        )
                        print(f"⏭️  Skipped {name} ({slug}) - already registered")
                        continue
                    except Exception:
                        # Connector doesn't exist, proceed with registration
                        pass

                # Register connector
                result = register_connector_direct(
                    session=session,
                    manifest_path=manifest_file,
                    dry_run=dry_run,
                )

                if result["status"] == "error":
                    results["errors"].append(result)
                    print(
                        f"❌ Error: {name} ({slug}) - {result.get('error', 'Unknown error')}"
                    )
                elif result["status"] == "validated":
                    results["registered"].append(result)
                    print(f"✅ Validated: {name} ({slug})")
                else:
                    results["registered"].append(result)
                    print(
                        f"✅ Registered: {name} ({slug}) v{result.get('version', 'N/A')}"
                    )

                # Commit after each registration
                if not dry_run:
                    session.commit()

            except Exception as e:
                error_result = {
                    "slug": slug,
                    "name": name if "name" in locals() else slug,
                    "error": str(e),
                }
                results["errors"].append(error_result)
                print(f"❌ Exception: {slug} - {str(e)}")
                if not dry_run:
                    session.rollback()

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Register connector manifests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (validate all manifests)
  python scripts/register_connectors.py --dry-run

  # Register all connectors
  python scripts/register_connectors.py

  # Register single connector
  python scripts/register_connectors.py --connector-slug gmail

  # Register by category
  python scripts/register_connectors.py --category "Communication & Collaboration"
        """,
    )

    parser.add_argument(
        "--manifests-dir",
        type=str,
        default=None,
        help="Directory containing manifest files (default: app/connectors/manifests)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate manifests without registering",
    )
    parser.add_argument(
        "--connector-slug",
        type=str,
        default=None,
        help="Register only a specific connector by slug",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Register only connectors in a specific category",
    )

    args = parser.parse_args()

    # Determine manifests directory
    if args.manifests_dir:
        manifests_dir = Path(args.manifests_dir)
    else:
        manifests_dir = (
            Path(__file__).parent.parent / "app" / "connectors" / "manifests"
        )

    if not manifests_dir.exists():
        print(f"Error: Manifests directory not found: {manifests_dir}")
        sys.exit(1)

    # Register connectors
    try:
        results = register_all_connectors(
            manifests_dir=manifests_dir,
            dry_run=args.dry_run,
            connector_slug=args.connector_slug,
            category=args.category,
        )

        if "error" in results:
            print(f"\n❌ Error: {results['error']}")
            sys.exit(1)

        # Print summary
        print(f"\n{'='*60}")
        print("Summary:")
        print(f"  Total: {results['total']}")
        print(
            f"  {'Validated' if args.dry_run else 'Registered'}: {len(results['registered'])}"
        )
        print(f"  Skipped: {len(results['skipped'])}")
        print(f"  Errors: {len(results['errors'])}")
        print(f"{'='*60}")

        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"]:
                print(
                    f"  - {error.get('name', error.get('slug'))}: {error.get('error')}"
                )
            sys.exit(1)

        if not args.dry_run:
            print(
                f"\n✅ Successfully registered {len(results['registered'])} connector(s)"
            )

    except KeyboardInterrupt:
        print("\n\n⚠️  Registration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
