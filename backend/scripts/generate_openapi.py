#!/usr/bin/env python3
"""
Generate OpenAPI Schema

Generates and exports the OpenAPI schema from the SynthralOS backend application.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def generate_openapi_schema():
    """Generate OpenAPI schema and save to file."""
    openapi_schema = app.openapi()
    
    # Save to JSON file
    output_path = Path(__file__).parent.parent / "openapi.json"
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"✅ OpenAPI schema generated: {output_path}")
    print(f"📊 Total endpoints: {len(openapi_schema.get('paths', {}))}")
    
    # Print summary by tag
    tags_summary = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, details in methods.items():
            if isinstance(details, dict) and "tags" in details:
                for tag in details["tags"]:
                    if tag not in tags_summary:
                        tags_summary[tag] = 0
                    tags_summary[tag] += 1
    
    print("\n📋 Endpoints by tag:")
    for tag, count in sorted(tags_summary.items()):
        print(f"  - {tag}: {count} endpoints")
    
    return output_path


if __name__ == "__main__":
    generate_openapi_schema()

