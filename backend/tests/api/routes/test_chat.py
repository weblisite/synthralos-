"""
Integration tests for Chat API endpoints

Tests chat message processing and WebSocket connections.
"""

from fastapi.testclient import TestClient


class TestChatAPI:
    """Test suite for chat API endpoints."""

    def test_send_chat_message_automation_mode(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test sending a chat message in automation mode."""
        message_data = {
            "message": "Create a workflow that sends an email",
            "mode": "automation",
        }

        response = client.post(
            "/api/v1/chat",
            json=message_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "content" in data or "message" in data

    def test_send_chat_message_agent_mode(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test sending a chat message in agent mode."""
        message_data = {
            "message": "Research the latest AI developments",
            "mode": "agent",
        }

        response = client.post(
            "/api/v1/chat",
            json=message_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "content" in data or "message" in data

    def test_send_chat_message_invalid_data(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test sending a chat message with invalid data."""
        invalid_data = {
            # Missing message field
        }

        response = client.post(
            "/api/v1/chat",
            json=invalid_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 422  # Validation error

    def test_send_chat_message_unauthorized(
        self,
        client: TestClient,
    ):
        """Test sending a chat message without authentication."""
        message_data = {
            "message": "Test message",
            "mode": "automation",
        }

        response = client.post(
            "/api/v1/chat",
            json=message_data,
        )

        assert response.status_code == 401  # Unauthorized
