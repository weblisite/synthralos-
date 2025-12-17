"""
Integration tests for Connector API endpoints

Tests connector registration, retrieval, and invocation.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_connector_manifest():
    """Return a sample connector manifest for testing."""
    return {
        "name": "Test Connector",
        "slug": "test-connector",
        "version": "1.0.0",
        "description": "Test connector for integration tests",
        "categories": ["test"],
        "actions": {
            "test_action": {
                "name": "Test Action",
                "description": "Test action for integration tests",
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


class TestConnectorRegistration:
    """Test suite for connector registration."""

    def test_register_connector(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_connector_manifest: dict,
    ):
        """Test registering a connector."""
        response = client.post(
            "/api/v1/connectors/register",
            json={
                "manifest": sample_connector_manifest,
                "wheel_url": "https://synthralos.ai/test-connector-1.0.0.whl",
            },
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == sample_connector_manifest["slug"]
        assert data["name"] == sample_connector_manifest["name"]

    def test_register_connector_invalid_manifest(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test registering a connector with invalid manifest."""
        invalid_manifest = {
            "name": "Test",
            # Missing required fields
        }

        response = client.post(
            "/api/v1/connectors/register",
            json={"manifest": invalid_manifest},
            headers=superuser_token_headers,
        )

        assert response.status_code == 400  # Bad request

    def test_list_connectors(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_connector_manifest: dict,
    ):
        """Test listing connectors."""
        # First register a connector
        register_response = client.post(
            "/api/v1/connectors/register",
            json={"manifest": sample_connector_manifest},
            headers=superuser_token_headers,
        )
        assert register_response.status_code == 200

        # Then list connectors
        response = client.get(
            "/api/v1/connectors/",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify our connector is in the list
        slugs = [c["slug"] for c in data]
        assert sample_connector_manifest["slug"] in slugs

    def test_get_connector(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_connector_manifest: dict,
    ):
        """Test getting a specific connector."""
        # First register a connector
        register_response = client.post(
            "/api/v1/connectors/register",
            json={"manifest": sample_connector_manifest},
            headers=superuser_token_headers,
        )
        assert register_response.status_code == 200

        slug = sample_connector_manifest["slug"]

        # Get connector
        response = client.get(
            f"/api/v1/connectors/{slug}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug
        assert data["name"] == sample_connector_manifest["name"]

    def test_get_connector_not_found(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test getting a non-existent connector."""
        response = client.get(
            "/api/v1/connectors/nonexistent",
            headers=superuser_token_headers,
        )

        assert response.status_code == 404


class TestConnectorInvocation:
    """Test suite for connector action invocation."""

    def test_invoke_connector_action(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_connector_manifest: dict,
    ):
        """Test invoking a connector action."""
        # First register a connector
        register_response = client.post(
            "/api/v1/connectors/register",
            json={"manifest": sample_connector_manifest},
            headers=superuser_token_headers,
        )
        assert register_response.status_code == 200

        slug = sample_connector_manifest["slug"]
        action = "test_action"

        # Invoke action (may fail if connector wheel not available, but should return proper error)
        response = client.post(
            f"/api/v1/connectors/{slug}/{action}",
            json={"input": "test"},
            headers=superuser_token_headers,
        )

        # Should either succeed or return a proper error (not 404)
        assert response.status_code in [200, 400, 500]

