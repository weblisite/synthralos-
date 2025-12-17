"""
Connector Registry Service

Manages connector registration, versioning, and manifest validation.
Handles connector discovery and metadata management.
"""

import uuid
from typing import Any

from sqlmodel import Session, select

from app.models import Connector, ConnectorVersion
from app.services.secrets import SecretsService, default_secrets_service


class ConnectorRegistryError(Exception):
    """Base exception for connector registry errors."""
    pass


class InvalidManifestError(ConnectorRegistryError):
    """Invalid connector manifest."""
    pass


class ConnectorNotFoundError(ConnectorRegistryError):
    """Connector not found."""
    pass


class ConnectorRegistry:
    """
    Connector registry service.
    
    Manages:
    - Connector registration
    - Manifest validation
    - Version management
    - Connector discovery
    """
    
    def __init__(self, secrets_service: SecretsService | None = None):
        """
        Initialize connector registry.
        
        Args:
            secrets_service: SecretsService instance for secret management
        """
        self.secrets_service = secrets_service or default_secrets_service
    
    def validate_manifest(self, manifest: dict[str, Any]) -> None:
        """
        Validate a connector manifest.
        
        Args:
            manifest: Connector manifest dictionary
            
        Raises:
            InvalidManifestError: If manifest is invalid
        """
        required_fields = [
            "name",
            "version",
            "slug",
            "description",
            "actions",
            "triggers",
        ]
        
        for field in required_fields:
            if field not in manifest:
                raise InvalidManifestError(f"Missing required field: {field}")
        
        # Validate slug format
        slug = manifest.get("slug", "")
        if not slug or not slug.replace("-", "").replace("_", "").isalnum():
            raise InvalidManifestError(
                "Slug must be alphanumeric with hyphens/underscores only"
            )
        
        # Validate version format (SemVer)
        version = manifest.get("version", "")
        if not self._is_valid_semver(version):
            raise InvalidManifestError(
                f"Invalid version format: {version}. Must be SemVer (e.g., 1.0.0)"
            )
        
        # Validate actions structure
        actions = manifest.get("actions", {})
        if not isinstance(actions, dict):
            raise InvalidManifestError("Actions must be a dictionary")
        
        for action_id, action_config in actions.items():
            if not isinstance(action_config, dict):
                raise InvalidManifestError(f"Action '{action_id}' must be a dictionary")
            if "name" not in action_config:
                raise InvalidManifestError(f"Action '{action_id}' missing 'name' field")
        
        # Validate triggers structure
        triggers = manifest.get("triggers", {})
        if not isinstance(triggers, dict):
            raise InvalidManifestError("Triggers must be a dictionary")
        
        for trigger_id, trigger_config in triggers.items():
            if not isinstance(trigger_config, dict):
                raise InvalidManifestError(f"Trigger '{trigger_id}' must be a dictionary")
            if "name" not in trigger_config:
                raise InvalidManifestError(f"Trigger '{trigger_id}' missing 'name' field")
    
    def _is_valid_semver(self, version: str) -> bool:
        """
        Check if version string is valid SemVer.
        
        Args:
            version: Version string
            
        Returns:
            True if valid SemVer, False otherwise
        """
        import re
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9-]+)?(\+[a-zA-Z0-9-]+)?$"
        return bool(re.match(semver_pattern, version))
    
    def register_connector(
        self,
        session: Session,
        manifest: dict[str, Any],
        wheel_url: str | None = None,
        owner_id: uuid.UUID | None = None,
        is_platform: bool = False,
        created_by: uuid.UUID | None = None,
    ) -> ConnectorVersion:
        """
        Register a new connector version.
        
        Args:
            session: Database session
            manifest: Connector manifest
            wheel_url: Optional wheel file URL
            owner_id: User ID who owns the connector (None for platform connectors)
            is_platform: True if connector is available to all users, False if user-specific
            created_by: User ID who created the connector
            
        Returns:
            ConnectorVersion instance
            
        Raises:
            InvalidManifestError: If manifest is invalid
        """
        # Validate manifest
        self.validate_manifest(manifest)
        
        slug = manifest["slug"]
        version = manifest["version"]
        
        # For platform connectors, slug must be unique globally
        # For user connectors, slug must be unique per owner
        if is_platform:
            # Platform connector: check global uniqueness
            connector = session.exec(
                select(Connector).where(
                    Connector.slug == slug,
                    Connector.is_platform == True,
                )
            ).first()
        else:
            # User connector: check uniqueness for this owner
            connector = session.exec(
                select(Connector).where(
                    Connector.slug == slug,
                    Connector.owner_id == owner_id,
                    Connector.is_platform == False,
                )
            ).first()
        
        if not connector:
            # Create new connector
            connector = Connector(
                slug=slug,
                name=manifest["name"],
                status=manifest.get("status", "draft"),
                owner_id=owner_id,
                is_platform=is_platform,
                created_by=created_by,
            )
            session.add(connector)
            session.commit()
            session.refresh(connector)
        
        # Check if version already exists
        existing_version = session.exec(
            select(ConnectorVersion).where(
                ConnectorVersion.connector_id == connector.id,
                ConnectorVersion.version == version,
            )
        ).first()
        
        if existing_version:
            raise ConnectorRegistryError(
                f"Connector '{slug}' version '{version}' already exists"
            )
        
        # Create connector version
        connector_version = ConnectorVersion(
            connector_id=connector.id,
            version=version,
            manifest=manifest,
            wheel_url=wheel_url,
        )
        
        session.add(connector_version)
        
        # Update connector's latest version if this is newer
        if not connector.latest_version_id or self._is_version_newer(
            version,
            self._get_version_string(session, connector.latest_version_id),
        ):
            connector.latest_version_id = connector_version.id
        
        session.add(connector)
        session.commit()
        session.refresh(connector_version)
        
        return connector_version
    
    def _get_version_string(self, session: Session, version_id: uuid.UUID) -> str:
        """Get version string from version ID."""
        version = session.get(ConnectorVersion, version_id)
        return version.version if version else "0.0.0"
    
    def _is_version_newer(self, version1: str, version2: str) -> bool:
        """
        Check if version1 is newer than version2.
        
        Args:
            version1: First version (SemVer)
            version2: Second version (SemVer)
            
        Returns:
            True if version1 > version2
        """
        def parse_version(v: str) -> tuple[int, int, int]:
            # Remove pre-release and build metadata
            base = v.split("-")[0].split("+")[0]
            parts = base.split(".")
            return (
                int(parts[0]) if len(parts) > 0 else 0,
                int(parts[1]) if len(parts) > 1 else 0,
                int(parts[2]) if len(parts) > 2 else 0,
            )
        
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        return v1 > v2
    
    def get_connector(
        self,
        session: Session,
        slug: str,
        version: str | None = None,
    ) -> ConnectorVersion:
        """
        Get a connector version.
        
        Args:
            session: Database session
            slug: Connector slug
            version: Version string (uses latest if None)
            
        Returns:
            ConnectorVersion instance
            
        Raises:
            ConnectorNotFoundError: If connector not found
        """
        connector = session.exec(
            select(Connector).where(Connector.slug == slug)
        ).first()
        
        if not connector:
            raise ConnectorNotFoundError(f"Connector '{slug}' not found")
        
        if version:
            # Get specific version
            connector_version = session.exec(
                select(ConnectorVersion).where(
                    ConnectorVersion.connector_id == connector.id,
                    ConnectorVersion.version == version,
                )
            ).first()
            
            if not connector_version:
                raise ConnectorNotFoundError(
                    f"Connector '{slug}' version '{version}' not found"
                )
        else:
            # Get latest version
            if not connector.latest_version_id:
                raise ConnectorNotFoundError(
                    f"Connector '{slug}' has no versions"
                )
            
            connector_version = session.get(
                ConnectorVersion,
                connector.latest_version_id,
            )
        
        return connector_version
    
    def list_connectors(
        self,
        session: Session,
        status: str | None = None,
        owner_id: uuid.UUID | None = None,
        is_platform: bool | None = None,
        include_user_connectors: bool = False,
        user_id: uuid.UUID | None = None,
    ) -> list[Connector]:
        """
        List connectors.
        
        Args:
            session: Database session
            status: Optional filter by status (draft, beta, stable, deprecated)
            owner_id: Filter by owner ID (None = platform connectors)
            is_platform: Filter by platform flag (True = platform, False = user-owned)
            include_user_connectors: If True and user_id provided, include user's custom connectors
            user_id: User ID to include custom connectors for
            
        Returns:
            List of Connector instances
        """
        query = select(Connector)
        
        if status:
            query = query.where(Connector.status == status)
        
        if is_platform is not None:
            query = query.where(Connector.is_platform == is_platform)
        
        if owner_id is not None:
            query = query.where(Connector.owner_id == owner_id)
        
        # If include_user_connectors is True, we want platform connectors OR user's connectors
        if include_user_connectors and user_id:
            from sqlalchemy import or_
            query = query.where(
                or_(
                    Connector.is_platform == True,
                    Connector.owner_id == user_id,
                )
            )
        
        connectors = session.exec(query).all()
        return list(connectors)
    
    def get_connector_actions(
        self,
        session: Session,
        slug: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """
        Get available actions for a connector.
        
        Args:
            session: Database session
            slug: Connector slug
            version: Version string (uses latest if None)
            
        Returns:
            Dictionary of action_id -> action_config
        """
        connector_version = self.get_connector(session, slug, version)
        return connector_version.manifest.get("actions", {})
    
    def get_connector_triggers(
        self,
        session: Session,
        slug: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """
        Get available triggers for a connector.
        
        Args:
            session: Database session
            slug: Connector slug
            version: Version string (uses latest if None)
            
        Returns:
            Dictionary of trigger_id -> trigger_config
        """
        connector_version = self.get_connector(session, slug, version)
        return connector_version.manifest.get("triggers", {})
    
    def update_connector_status(
        self,
        session: Session,
        slug: str,
        status: str,
    ) -> Connector:
        """
        Update connector status.
        
        Args:
            session: Database session
            slug: Connector slug
            status: New status (draft, beta, stable, deprecated)
            
        Returns:
            Updated Connector instance
        """
        connector = session.exec(
            select(Connector).where(Connector.slug == slug)
        ).first()
        
        if not connector:
            raise ConnectorNotFoundError(f"Connector '{slug}' not found")
        
        valid_statuses = ["draft", "beta", "stable", "deprecated"]
        if status not in valid_statuses:
            raise ConnectorRegistryError(
                f"Invalid status: {status}. Must be one of: {valid_statuses}"
            )
        
        connector.status = status
        session.add(connector)
        session.commit()
        session.refresh(connector)
        
        return connector


# Default connector registry instance
default_connector_registry = ConnectorRegistry()

