"""
Integration tests for Workflow API endpoints

Tests workflow CRUD operations and execution endpoints.
"""

import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Workflow, WorkflowExecution, User


@pytest.fixture
def sample_workflow_data():
    """Return sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "description": "Integration test workflow",
        "is_active": True,
        "trigger_config": {
            "type": "manual",
        },
        "graph_config": {
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "trigger",
                    "config": {"trigger_type": "manual"},
                },
                {
                    "id": "code-1",
                    "type": "code",
                    "config": {"code": "result = 42"},
                },
            ],
            "edges": [{"source": "trigger-1", "target": "code-1"}],
        },
    }


@pytest.fixture
def created_workflow(
    client: TestClient, superuser_token_headers: dict[str, str], sample_workflow_data
):
    """Create a workflow and return its data."""
    response = client.post(
        "/api/v1/workflows/",
        json=sample_workflow_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    return response.json()


class TestWorkflowCRUD:
    """Test suite for workflow CRUD operations."""

    def test_create_workflow(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_workflow_data,
    ):
        """Test creating a workflow."""
        response = client.post(
            "/api/v1/workflows/",
            json=sample_workflow_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_workflow_data["name"]
        assert data["description"] == sample_workflow_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_create_workflow_invalid_data(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test creating a workflow with invalid data."""
        invalid_data = {
            "name": "Test",
            # Missing required fields
        }

        response = client.post(
            "/api/v1/workflows/",
            json=invalid_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 422  # Validation error

    def test_read_workflow(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test reading a workflow."""
        workflow_id = created_workflow["id"]

        response = client.get(
            f"/api/v1/workflows/{workflow_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workflow_id
        assert data["name"] == created_workflow["name"]

    def test_read_workflow_not_found(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test reading a non-existent workflow."""
        fake_id = str(uuid.uuid4())

        response = client.get(
            f"/api/v1/workflows/{fake_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 404

    def test_read_workflows(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test listing workflows."""
        response = client.get(
            "/api/v1/workflows/",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # Verify our created workflow is in the list
        workflow_ids = [w["id"] for w in data["data"]]
        assert created_workflow["id"] in workflow_ids

    def test_update_workflow(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test updating a workflow."""
        workflow_id = created_workflow["id"]
        update_data = {
            "name": "Updated Workflow Name",
            "description": "Updated description",
        }

        response = client.put(
            f"/api/v1/workflows/{workflow_id}",
            json=update_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_delete_workflow(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test deleting a workflow."""
        workflow_id = created_workflow["id"]

        response = client.delete(
            f"/api/v1/workflows/{workflow_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200

        # Verify workflow is deleted
        get_response = client.get(
            f"/api/v1/workflows/{workflow_id}",
            headers=superuser_token_headers,
        )
        assert get_response.status_code == 404


class TestWorkflowExecution:
    """Test suite for workflow execution endpoints."""

    def test_run_workflow(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test running a workflow."""
        workflow_id = created_workflow["id"]
        trigger_data = {"test": "data"}

        response = client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            json={"trigger_data": trigger_data},
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "status" in data

    def test_run_workflow_not_found(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test running a non-existent workflow."""
        fake_id = str(uuid.uuid4())

        response = client.post(
            f"/api/v1/workflows/{fake_id}/run",
            json={"trigger_data": {}},
            headers=superuser_token_headers,
        )

        assert response.status_code == 404

    def test_get_workflow_executions(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test getting workflow executions."""
        workflow_id = created_workflow["id"]

        # First, run the workflow to create an execution
        run_response = client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            json={"trigger_data": {}},
            headers=superuser_token_headers,
        )
        assert run_response.status_code == 200

        # Then get executions
        response = client.get(
            f"/api/v1/workflows/{workflow_id}/executions",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_get_execution_status(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test getting execution status."""
        workflow_id = created_workflow["id"]

        # Run workflow to create execution
        run_response = client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            json={"trigger_data": {}},
            headers=superuser_token_headers,
        )
        assert run_response.status_code == 200
        execution_id = run_response.json()["execution_id"]

        # Get execution status
        response = client.get(
            f"/api/v1/executions/{execution_id}/status",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "status" in data
        assert "workflow_id" in data

    def test_replay_execution(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        created_workflow: dict,
    ):
        """Test replaying a workflow execution."""
        workflow_id = created_workflow["id"]

        # Run workflow to create execution
        run_response = client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            json={"trigger_data": {}},
            headers=superuser_token_headers,
        )
        assert run_response.status_code == 200
        execution_id = run_response.json()["execution_id"]

        # Replay execution
        response = client.post(
            f"/api/v1/executions/{execution_id}/replay",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        # Should be a new execution ID
        assert data["execution_id"] != execution_id

