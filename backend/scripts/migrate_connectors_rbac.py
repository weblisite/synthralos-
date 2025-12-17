"""
Migration script to add RBAC fields to existing connectors.

This script updates all existing connectors to be platform connectors
(is_platform=True, owner_id=None) since they were created before RBAC was implemented.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.db import engine
from app.models import Connector
from sqlmodel import Session, select


def migrate_connectors():
    """Migrate existing connectors to have RBAC fields."""
    with Session(engine) as session:
        # Get all connectors
        connectors = session.exec(select(Connector)).all()
        
        updated_count = 0
        for connector in connectors:
            # Check if connector already has RBAC fields set
            # If owner_id is None and is_platform is not explicitly False, set as platform
            if connector.owner_id is None:
                connector.is_platform = True
                connector.created_by = None  # Platform connectors have no creator
                session.add(connector)
                updated_count += 1
        
        session.commit()
        print(f"✅ Updated {updated_count} connector(s) to be platform connectors")
        
        # Verify migration
        platform_count = session.exec(
            select(Connector).where(Connector.is_platform == True)
        ).all()
        print(f"✅ Total platform connectors: {len(platform_count)}")


if __name__ == "__main__":
    print("Starting connector RBAC migration...")
    migrate_connectors()
    print("Migration completed!")

