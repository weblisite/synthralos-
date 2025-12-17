"""
Unit tests for Connector Registry

Tests connector registry functionality including:
- Connector registration
- Manifest validation
- Version management
- Connector retrieval
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.connectors.registry import (
    ConnectorNotFoundError,
    ConnectorRegistry,
    InvalidManifestError,
)
from app.models import Connector, ConnectorVersion


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def connector_registry():
    """Create a ConnectorRegistry instance for testing."""
    return ConnectorRegistry()


@pytest.fixture
def valid_manifest():
    """Return a valid connector manifest."""
    return {
        "name": "Test Connector",
        "slug": "test-connector",
        "version": "1.0.0",
        "description": "Test connector for unit tests",
        "categories": ["test"],
        "actions": {
            "test_action": {
                "name": "Test Action",
                "description": "Test action",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"},
                    },
                    "required": ["input"],
                },
            }
        },
        "triggers": {},
    }


class TestConnectorRegistry:
    """Test suite for ConnectorRegistry."""

    def test_register_connector_success(
        self, connector_registry, db_session, valid_manifest
    ):
        """Test successful connector registration."""
        connector = connector_registry.register_connector(
            db_session,
            manifest=valid_manifest,
            wheel_url="https://synthralos.ai/test-connector-1.0.0.whl",
        )

        assert connector is not None
        assert isinstance(connector, Connector)
        assert connector.slug == "test-connector"
        assert connector.name == "Test Connector"

        # Verify version was created
        from sqlmodel import select
        versions = db_session.exec(
            select(ConnectorVersion).where(
                ConnectorVersion.connector_id == connector.id
            )
        ).all()
        assert len(versions) == 1
        assert versions[0].version == "1.0.0"

    def test_register_connector_invalid_manifest(
        self, connector_registry, db_session
    ):
        """Test connector registration with invalid manifest."""
        invalid_manifest = {
            "name": "Test",
            # Missing required fields: slug, version, description
        }

        with pytest.raises(InvalidManifestError):
            connector_registry.register_connector(
                db_session,
                manifest=invalid_manifest,
            )

    def test_register_connector_duplicate_slug(
        self, connector_registry, db_session, valid_manifest
    ):
        """Test registering connector with duplicate slug."""
        # Register first connector
        connector_registry.register_connector(
            db_session, manifest=valid_manifest
        )

        # Try to register again with same slug
        duplicate_manifest = valid_manifest.copy()
        duplicate_manifest["version"] = "2.0.0"

        # Should update existing connector or raise error (implementation dependent)
        # This test verifies the behavior
        result = connector_registry.register_connector(
            db_session, manifest=duplicate_manifest
        )

        assert result is not None

    def test_get_connector_success(
        self, connector_registry, db_session, valid_manifest
    ):
        """Test retrieving a connector."""
        connector = connector_registry.register_connector(
            db_session, manifest=valid_manifest
        )

        retrieved = connector_registry.get_connector(
            db_session, slug="test-connector"
        )

        assert retrieved is not None
        assert retrieved.id == connector.id
        assert retrieved.slug == "test-connector"

    def test_get_connector_not_found(
        self, connector_registry, db_session
    ):
        """Test retrieving non-existent connector."""
        with pytest.raises(ConnectorNotFoundError):
            connector_registry.get_connector(db_session, slug="nonexistent")

    def test_list_connectors(
        self, connector_registry, db_session, valid_manifest
    ):
        """Test listing connectors."""
        # Register multiple connectors
        connector1 = connector_registry.register_connector(
            db_session, manifest=valid_manifest
        )

        manifest2 = valid_manifest.copy()
        manifest2["slug"] = "test-connector-2"
        manifest2["name"] = "Test Connector 2"
        connector2 = connector_registry.register_connector(
            db_session, manifest=manifest2
        )

        connectors = connector_registry.list_connectors(db_session)

        assert len(connectors) >= 2
        slugs = [c.slug for c in connectors]
        assert "test-connector" in slugs
        assert "test-connector-2" in slugs

    def test_update_connector_status(
        self, connector_registry, db_session, valid_manifest
    ):
        """Test updating connector status."""
        connector = connector_registry.register_connector(
            db_session, manifest=valid_manifest
        )

        updated = connector_registry.update_connector_status(
            db_session, slug="test-connector", new_status="deprecated"
        )

        assert updated is not None
        assert updated.status == "deprecated"

    def test_get_connector_version(
        self, connector_registry, db_session, valid_manifest
    ):
        """Test retrieving specific connector version."""
        connector = connector_registry.register_connector(
            db_session, manifest=valid_manifest
        )

        version = connector_registry.get_connector_version(
            db_session, slug="test-connector", version="1.0.0"
        )

        assert version is not None
        assert version.version == "1.0.0"
        assert version.connector_id == connector.id

    def test_validate_manifest_success(
        self, connector_registry, valid_manifest
    ):
        """Test manifest validation with valid manifest."""
        # Should not raise an exception
        connector_registry.validate_manifest(valid_manifest)

    def test_validate_manifest_missing_fields(
        self, connector_registry
    ):
        """Test manifest validation with missing required fields."""
        invalid_manifest = {
            "name": "Test",
            # Missing slug, version, description
        }

        with pytest.raises(InvalidManifestError):
            connector_registry.validate_manifest(invalid_manifest)

    def test_validate_manifest_invalid_slug(
        self, connector_registry
    ):
        """Test manifest validation with invalid slug format."""
        invalid_manifest = {
            "name": "Test Connector",
            "slug": "Invalid Slug!",  # Invalid: contains spaces and special chars
            "version": "1.0.0",
            "description": "Test",
            "actions": {},
            "triggers": {},
        }

        with pytest.raises(InvalidManifestError):
            connector_registry.validate_manifest(invalid_manifest)

    def test_validate_manifest_invalid_version(
        self, connector_registry
    ):
        """Test manifest validation with invalid version format."""
        invalid_manifest = {
            "name": "Test Connector",
            "slug": "test-connector",
            "version": "invalid-version",  # Invalid: not SemVer
            "description": "Test",
            "actions": {},
            "triggers": {},
        }

        with pytest.raises(InvalidManifestError):
            connector_registry.validate_manifest(invalid_manifest)

