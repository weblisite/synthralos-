"""
Admin Connector Management API Routes

Endpoints for platform admins to manage connectors.
Requires is_superuser = True
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import User
from app.connectors.registry import (
    ConnectorNotFoundError,
    ConnectorRegistryError,
    InvalidManifestError,
    default_connector_registry,
)
from app.models import Connector, ConnectorVersion

router = APIRouter(prefix="/admin/connectors", tags=["admin", "connectors"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_platform_connector(
    *,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
    manifest: dict[str, Any],
    wheel_url: str | None = None,
) -> Any:
    """
    Register a new platform connector (admin only).
    
    Platform connectors are available to all users.
    
    Requires:
    - is_superuser = True
    - Valid connector manifest
    - Optional wheel file URL
    
    Returns:
    - ConnectorVersion details
    """
    registry = default_connector_registry
    
    try:
        connector_version = registry.register_connector(
            session=session,
            manifest=manifest,
            wheel_url=wheel_url,
            owner_id=None,  # Platform connectors have no owner
            is_platform=True,
            created_by=current_user.id,
        )
        
        return {
            "id": str(connector_version.id),
            "connector_id": str(connector_version.connector_id),
            "version": connector_version.version,
            "slug": manifest.get("slug"),
            "name": manifest.get("name"),
            "is_platform": True,
            "owner_id": None,
            "created_at": connector_version.created_at.isoformat(),
        }
    except InvalidManifestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid manifest: {str(e)}",
        )
    except ConnectorRegistryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/list")
def list_all_connectors(
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
    status_filter: str | None = None,
    is_platform: bool | None = None,
    category: str | None = None,
) -> Any:
    """
    List all connectors (admin only).
    
    Can filter by platform/user connectors, status, and category.
    
    Requires:
    - is_superuser = True
    
    Query Parameters:
    - status_filter: Optional filter by status
    - is_platform: Filter by platform flag (True/False/None for all)
    - category: Optional filter by category
    
    Returns:
    - List of all connectors with metadata
    """
    registry = default_connector_registry
    
    connectors = registry.list_connectors(
        session=session,
        status=status_filter,
        is_platform=is_platform,
    )
    
    result = []
    for connector in connectors:
        # Get latest version info
        latest_version = None
        if connector.latest_version_id:
            latest_version = session.get(ConnectorVersion, connector.latest_version_id)
        
        # Extract metadata from manifest
        manifest = latest_version.manifest if latest_version else {}
        connector_category = manifest.get("category", "Uncategorized")
        description = manifest.get("description", "")
        
        # Filter by category if specified
        if category and connector_category != category:
            continue
        
        result.append({
            "id": str(connector.id),
            "slug": connector.slug,
            "name": connector.name,
            "status": connector.status,
            "category": connector_category,
            "description": description,
            "latest_version": latest_version.version if latest_version else None,
            "is_platform": connector.is_platform,
            "owner_id": str(connector.owner_id) if connector.owner_id else None,
            "created_by": str(connector.created_by) if connector.created_by else None,
            "created_at": connector.created_at.isoformat(),
        })
    
    return {
        "connectors": result,
        "total_count": len(result),
    }


@router.patch("/{slug}/status")
def update_connector_status(
    slug: str,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
    new_status: str = "beta",
) -> Any:
    """
    Update connector status (admin only).
    
    Requires:
    - is_superuser = True
    
    Path Parameters:
    - slug: Connector slug
    
    Query Parameters:
    - new_status: New status (draft, beta, stable, deprecated)
    
    Returns:
    - Updated connector
    """
    registry = default_connector_registry
    
    valid_statuses = ["draft", "beta", "stable", "deprecated"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )
    
    try:
        connector = session.exec(
            select(Connector).where(Connector.slug == slug)
        ).first()
        
        if not connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector '{slug}' not found",
            )
        
        connector.status = new_status
        session.add(connector)
        session.commit()
        session.refresh(connector)
        
        return {
            "slug": connector.slug,
            "name": connector.name,
            "status": connector.status,
            "updated_at": connector.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{slug}")
def delete_connector(
    slug: str,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete a connector (admin only).
    
    Requires:
    - is_superuser = True
    
    Path Parameters:
    - slug: Connector slug
    
    Returns:
    - Success status
    """
    try:
        connector = session.exec(
            select(Connector).where(Connector.slug == slug)
        ).first()
        
        if not connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector '{slug}' not found",
            )
        
        # Only allow deleting user-owned connectors or deprecated platform connectors
        if connector.is_platform and connector.status != "deprecated":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete active platform connectors. Deprecate first.",
            )
        
        session.delete(connector)
        session.commit()
        
        return {
            "success": True,
            "message": f"Connector '{slug}' deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/stats")
def get_connector_statistics(
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get connector statistics (admin only).
    
    Requires:
    - is_superuser = True
    
    Returns:
    - Statistics about connectors
    """
    registry = default_connector_registry
    
    # Get all connectors
    all_connectors = registry.list_connectors(session=session)
    platform_connectors = registry.list_connectors(session=session, is_platform=True)
    user_connectors = registry.list_connectors(session=session, is_platform=False)
    
    # Count by status
    status_counts = {}
    for connector in all_connectors:
        status_counts[connector.status] = status_counts.get(connector.status, 0) + 1
    
    # Count by category
    category_counts = {}
    for connector in all_connectors:
        if connector.latest_version_id:
            latest_version = session.get(ConnectorVersion, connector.latest_version_id)
            if latest_version:
                manifest = latest_version.manifest
                category = manifest.get("category", "Uncategorized")
                category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        "total_connectors": len(all_connectors),
        "platform_connectors": len(platform_connectors),
        "user_connectors": len(user_connectors),
        "by_status": status_counts,
        "by_category": category_counts,
    }

