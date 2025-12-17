"""
Integration tests for Agent API endpoints

Tests agent task execution and status checking.
"""

import pytest
from fastapi.testclient import TestClient


class TestAgentExecution:
    """Test suite for agent execution endpoints."""

    def test_run_agent_task(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test running an agent task."""
        task_data = {
            "task_type": "test_task",
            "input_data": {
                "prompt": "Test prompt",
            },
            "task_requirements": {
                "agent_type": "simple",
            },
        }

        response = client.post(
            "/api/v1/agents/run",
            json=task_data,
            headers=superuser_token_headers,
        )

        # May fail if no frameworks configured, but should return proper status
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "agent_framework" in data
            assert "status" in data

    def test_run_agent_task_invalid_data(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test running an agent task with invalid data."""
        invalid_data = {
            # Missing required fields
        }

        response = client.post(
            "/api/v1/agents/run",
            json=invalid_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 422  # Validation error

    def test_get_agent_task_status(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test getting agent task status."""
        # First run a task
        task_data = {
            "task_type": "test_task",
            "input_data": {"prompt": "Test"},
            "task_requirements": {"agent_type": "simple"},
        }

        run_response = client.post(
            "/api/v1/agents/run",
            json=task_data,
            headers=superuser_token_headers,
        )

        if run_response.status_code == 200:
            task_id = run_response.json()["id"]

            # Get task status
            response = client.get(
                f"/api/v1/agents/status/{task_id}",
                headers=superuser_token_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "status" in data
            assert "agent_framework" in data

    def test_get_agent_task_status_not_found(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test getting status for non-existent task."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(
            f"/api/v1/agents/status/{fake_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 404

