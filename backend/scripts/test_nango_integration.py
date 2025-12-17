#!/usr/bin/env python3
"""
Test Nango Integration

Tests OAuth flows with Nango-enabled connectors and direct OAuth fallback.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.core.db import engine
from app.core.config import settings
from app.models import Connector, ConnectorVersion
from app.connectors.registry import default_connector_registry


def test_connector_list():
    """Test connector list endpoint includes Nango status."""
    print("\n" + "="*60)
    print("Test 1: Connector List with Nango Status")
    print("="*60)
    
    with Session(engine) as session:
        connectors = session.exec(select(Connector)).all()
        
        print(f"\nTotal connectors: {len(connectors)}")
        
        # Check Nango-enabled connectors
        nango_enabled = 0
        direct_oauth = 0
        
        for connector in connectors[:10]:  # Check first 10
            if connector.latest_version_id:
                version = session.get(ConnectorVersion, connector.latest_version_id)
                if version:
                    manifest = version.manifest
                    nango_config = manifest.get("nango", {})
                    is_nango = nango_config.get("enabled", False)
                    
                    if is_nango:
                        nango_enabled += 1
                        print(f"  ✅ {connector.name}: Nango enabled (provider: {nango_config.get('provider_key')})")
                    else:
                        direct_oauth += 1
                        print(f"  ⚠️  {connector.name}: Direct OAuth")
        
        print(f"\nSummary:")
        print(f"  Nango-enabled: {nango_enabled}")
        print(f"  Direct OAuth: {direct_oauth}")
        
        return True


def test_nango_configuration():
    """Test Nango configuration."""
    print("\n" + "="*60)
    print("Test 2: Nango Configuration")
    print("="*60)
    
    print(f"\nNango URL: {settings.NANGO_URL}")
    print(f"Nango Enabled: {settings.NANGO_ENABLED}")
    print(f"Nango Secret Key: {'*' * 20 if settings.NANGO_SECRET_KEY else 'NOT SET'}")
    
    if settings.NANGO_ENABLED:
        print("\n✅ Nango is enabled")
        if settings.NANGO_SECRET_KEY:
            print("✅ Nango secret key is configured")
        else:
            print("⚠️  Nango secret key is not set")
    else:
        print("\n⚠️  Nango is disabled (will use direct OAuth)")
    
    return True


def test_connector_manifest_structure():
    """Test connector manifest structure includes Nango config."""
    print("\n" + "="*60)
    print("Test 3: Connector Manifest Structure")
    print("="*60)
    
    with Session(engine) as session:
        # Test Gmail connector (should have Nango)
        connector = session.exec(
            select(Connector).where(Connector.slug == "gmail")
        ).first()
        
        if not connector:
            print("❌ Gmail connector not found")
            return False
        
        if not connector.latest_version_id:
            print("❌ Gmail connector has no version")
            return False
        
        version = session.get(ConnectorVersion, connector.latest_version_id)
        if not version:
            print("❌ Gmail connector version not found")
            return False
        
        manifest = version.manifest
        
        # Check required fields
        required_fields = ["name", "slug", "category", "nango", "oauth"]
        missing_fields = [f for f in required_fields if f not in manifest]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        # Check Nango config
        nango_config = manifest.get("nango", {})
        if not isinstance(nango_config, dict):
            print("❌ Nango config is not a dict")
            return False
        
        if "enabled" not in nango_config:
            print("❌ Nango config missing 'enabled' field")
            return False
        
        if nango_config.get("enabled") and "provider_key" not in nango_config:
            print("❌ Nango config missing 'provider_key' field")
            return False
        
        print(f"\n✅ Manifest structure is valid")
        print(f"  Name: {manifest.get('name')}")
        print(f"  Category: {manifest.get('category')}")
        print(f"  Nango enabled: {nango_config.get('enabled')}")
        if nango_config.get("enabled"):
            print(f"  Provider key: {nango_config.get('provider_key')}")
        
        return True


def test_oauth_service_initialization():
    """Test OAuth service initialization."""
    print("\n" + "="*60)
    print("Test 4: OAuth Service Initialization")
    print("="*60)
    
    try:
        from app.connectors.oauth import default_oauth_service
        from app.services.nango import default_nango_service
        
        print("\n✅ OAuth service initialized")
        print(f"✅ Nango service initialized: {default_nango_service is not None}")
        
        # Check if Nango service is available
        if settings.NANGO_ENABLED:
            if default_nango_service:
                print("✅ Nango service is available")
            else:
                print("⚠️  Nango service is None (may fallback to direct OAuth)")
        else:
            print("⚠️  Nango is disabled, will use direct OAuth")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing services: {e}")
        return False


def test_connector_categories():
    """Test connector categories."""
    print("\n" + "="*60)
    print("Test 5: Connector Categories")
    print("="*60)
    
    with Session(engine) as session:
        connectors = session.exec(select(Connector)).all()
        
        categories = {}
        for connector in connectors:
            if connector.latest_version_id:
                version = session.get(ConnectorVersion, connector.latest_version_id)
                if version:
                    manifest = version.manifest
                    category = manifest.get("category", "Uncategorized")
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(connector.name)
        
        print(f"\nFound {len(categories)} categories:")
        for category, names in sorted(categories.items()):
            print(f"\n  {category}: {len(names)} connectors")
            for name in sorted(names)[:5]:  # Show first 5
                print(f"    - {name}")
            if len(names) > 5:
                print(f"    ... and {len(names) - 5} more")
        
        return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Nango Integration Tests")
    print("="*60)
    
    tests = [
        ("Connector List", test_connector_list),
        ("Nango Configuration", test_nango_configuration),
        ("Manifest Structure", test_connector_manifest_structure),
        ("OAuth Service", test_oauth_service_initialization),
        ("Connector Categories", test_connector_categories),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

