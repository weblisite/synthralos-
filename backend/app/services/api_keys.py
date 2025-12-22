"""
API Key Management Service

Handles user API key storage, retrieval, validation, and encryption.
Uses Infisical for encrypted storage.
"""

import hashlib
import logging
import uuid

from sqlmodel import Session, select

from app.services.secrets import SecretsService, default_secrets_service

logger = logging.getLogger(__name__)

# Service definitions with validation endpoints
# Only includes services that are actually integrated and used in the platform
SERVICE_DEFINITIONS = {
    # LLM Providers (actually used in chat_processor.py and agent frameworks)
    "openai": {
        "display_name": "OpenAI",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://api.openai.com/v1/models",
        "validation_method": "GET",
    },
    "anthropic": {
        "display_name": "Anthropic Claude",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://api.anthropic.com/v1/messages",
        "validation_method": "POST",
    },
    "google-ai": {
        "display_name": "Google AI (Gemini)",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://generativelanguage.googleapis.com/v1/models",
        "validation_method": "GET",
    },
    "cohere": {
        "display_name": "Cohere",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://api.cohere.ai/v1/models",
        "validation_method": "GET",
    },
    "huggingface": {
        "display_name": "Hugging Face",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://api-inference.huggingface.co/models",
        "validation_method": "GET",
    },
    "replicate": {
        "display_name": "Replicate",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://api.replicate.com/v1/models",
        "validation_method": "GET",
    },
    # OCR Services (actually used in OCR service)
    "google-vision": {
        "display_name": "Google Vision API",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://vision.googleapis.com/v1/images:annotate",
        "validation_method": "POST",
    },
    # Social Media (actually used in OSINT service and connector manifests)
    "twitter": {
        "display_name": "Twitter/X",
        "credential_types": ["bearer_token", "api_key_secret", "oauth"],
        "validation_endpoint": "https://api.twitter.com/2/tweets",
        "validation_method": "GET",
    },
    "reddit": {
        "display_name": "Reddit",
        "credential_types": ["oauth"],
        "validation_endpoint": "https://oauth.reddit.com/api/v1/me",
        "validation_method": "GET",
    },
    "linkedin": {
        "display_name": "LinkedIn",
        "credential_types": ["oauth"],
        "validation_endpoint": "https://api.linkedin.com/v2/me",
        "validation_method": "GET",
    },
    # Code Execution (actually used in code execution service)
    "e2b": {
        "display_name": "E2B (Code Sandbox)",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://api.e2b.dev/v1/sandboxes",
        "validation_method": "GET",
    },
    # Vector Databases (actually used in RAG service)
    "chromadb": {
        "display_name": "ChromaDB",
        "credential_types": ["auth_token"],
        "validation_endpoint": "",  # ChromaDB validation varies by deployment
        "validation_method": "GET",
    },
    "weaviate": {
        "display_name": "Weaviate",
        "credential_types": ["api_key"],
        "validation_endpoint": "",  # Weaviate validation varies by deployment
        "validation_method": "GET",
    },
    # Observability (actually used - LangSmith in dependencies)
    "langsmith": {
        "display_name": "LangSmith",
        "credential_types": ["api_key"],
        "validation_endpoint": "https://api.smith.langchain.com/v1/datasets",
        "validation_method": "GET",
    },
    # Storage (actually used - connector manifests exist)
    "aws-s3": {
        "display_name": "AWS S3",
        "credential_types": ["access_key_secret"],
        "validation_endpoint": "",  # S3 validation varies by region
        "validation_method": "GET",
    },
    "azure-blob": {
        "display_name": "Azure Blob Storage",
        "credential_types": ["connection_string"],
        "validation_endpoint": "",  # Azure validation varies by account
        "validation_method": "GET",
    },
}


class APIKeyServiceError(Exception):
    """Base exception for API key service errors."""

    pass


class InvalidAPIKeyError(APIKeyServiceError):
    """Invalid API key."""

    pass


class APIKeyService:
    """
    API key management service.

    Handles:
    - API key encryption and storage in Infisical
    - API key retrieval and decryption
    - API key validation
    - Key resolution (user key → platform default)
    """

    def __init__(self, secrets_service: SecretsService | None = None):
        """Initialize API key service."""
        self.secrets_service = secrets_service or default_secrets_service

    def hash_key(self, key: str) -> str:
        """
        Generate SHA256 hash of API key for verification.

        Args:
            key: API key string

        Returns:
            SHA256 hash (hex string)
        """
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def mask_key(self, key: str) -> str:
        """
        Mask API key for display (shows only last 4 characters).

        Args:
            key: API key string

        Returns:
            Masked key string (e.g., "sk-...xyz1")
        """
        if len(key) <= 4:
            return "*" * len(key)
        return f"{key[:4]}...{key[-4:]}"

    def get_infisical_path(
        self, user_id: str, service_name: str, credential_type: str | None = None
    ) -> str:
        """
        Generate Infisical path for API key storage.

        Args:
            user_id: User ID
            service_name: Service name (e.g., "openai")
            credential_type: Credential type (e.g., "api_key", "bearer_token")

        Returns:
            Infisical path string
        """
        base_path = f"/users/{user_id}/api-keys/{service_name}"
        if credential_type:
            return f"{base_path}/{credential_type}"
        return base_path

    def store_api_key(
        self,
        user_id: str,
        service_name: str,
        api_key: str,
        credential_type: str | None = None,
        additional_credentials: dict[str, str] | None = None,
    ) -> str:
        """
        Store API key in Infisical (encrypted).

        Args:
            user_id: User ID
            service_name: Service name
            api_key: API key to store
            credential_type: Credential type
            additional_credentials: Additional credentials (e.g., api_secret for Twitter)

        Returns:
            Infisical path where key is stored
        """
        path = self.get_infisical_path(user_id, service_name, credential_type)

        # Store main API key
        secret_key = f"user_{user_id}_{service_name}_{credential_type or 'api_key'}"

        # Combine all credentials into a JSON string
        credentials_data = {"api_key": api_key}
        if additional_credentials:
            credentials_data.update(additional_credentials)

        import json

        credentials_json = json.dumps(credentials_data)

        # Store in Infisical
        self.secrets_service.store_secret(
            secret_key=secret_key,
            secret_value=credentials_json,
            environment="prod",
            path=path,
        )

        logger.info(f"Stored API key for user {user_id}, service {service_name}")
        return path

    def retrieve_api_key(
        self,
        user_id: str,
        service_name: str,
        credential_type: str | None = None,
    ) -> dict[str, str] | None:
        """
        Retrieve API key from Infisical (decrypted).

        Args:
            user_id: User ID
            service_name: Service name
            credential_type: Credential type

        Returns:
            Dictionary with credentials (e.g., {"api_key": "...", "api_secret": "..."})
            or None if not found
        """
        path = self.get_infisical_path(user_id, service_name, credential_type)
        secret_key = f"user_{user_id}_{service_name}_{credential_type or 'api_key'}"

        try:
            credentials_json = self.secrets_service.get_secret(
                secret_key=secret_key,
                environment="prod",
                path=path,
            )

            if not credentials_json:
                return None

            import json

            return json.loads(credentials_json)
        except Exception as e:
            logger.error(f"Failed to retrieve API key: {e}")
            return None

    def delete_api_key(
        self,
        user_id: str,
        service_name: str,
        credential_type: str | None = None,
    ) -> None:
        """
        Delete API key from Infisical.

        Args:
            user_id: User ID
            service_name: Service name
            credential_type: Credential type
        """
        path = self.get_infisical_path(user_id, service_name, credential_type)
        secret_key = f"user_{user_id}_{service_name}_{credential_type or 'api_key'}"

        try:
            self.secrets_service.delete_secret(
                secret_key=secret_key,
                environment="prod",
                path=path,
            )
            logger.info(f"Deleted API key for user {user_id}, service {service_name}")
        except Exception as e:
            logger.error(f"Failed to delete API key: {e}")

    def validate_api_key(
        self, service_name: str, api_key: str, credential_type: str | None = None
    ) -> bool:
        """
        Validate API key by making a test API call.

        Args:
            service_name: Service name
            api_key: API key to validate
            credential_type: Credential type

        Returns:
            True if valid, False otherwise
        """
        if service_name not in SERVICE_DEFINITIONS:
            logger.warning(f"Unknown service: {service_name}")
            return False

        service_def = SERVICE_DEFINITIONS[service_name]

        try:
            import httpx

            headers = {}

            # Set authentication header based on service
            if service_name == "openai":
                headers["Authorization"] = f"Bearer {api_key}"
            elif service_name == "anthropic":
                headers["x-api-key"] = api_key
                headers["anthropic-version"] = "2023-06-01"
            elif service_name in ["google-ai", "google-vision"]:
                # Google services use query parameter
                pass
            elif service_name in [
                "cohere",
                "huggingface",
                "replicate",
                "e2b",
                "langsmith",
            ]:
                headers["Authorization"] = f"Bearer {api_key}"
            elif service_name == "twitter":
                if credential_type == "bearer_token":
                    headers["Authorization"] = f"Bearer {api_key}"
                # For OAuth, validation is more complex
                return True  # Skip validation for OAuth
            elif service_name in ["reddit", "linkedin"]:
                # OAuth services - skip validation
                return True
            elif service_name in ["chromadb", "weaviate"]:
                # Services with variable validation endpoints - skip validation
                return True
            elif service_name == "aws-s3":
                # AWS services require signature - skip validation
                return True
            elif service_name == "azure-blob":
                # Azure services require specific headers - skip validation
                return True

            # Make validation request
            url = service_def["validation_endpoint"]
            method = service_def.get("validation_method", "GET")

            # Add API key as query parameter for Google services
            if service_name in ["google-ai", "google-vision"]:
                if "?" in url:
                    url += f"&key={api_key}"
                else:
                    url += f"?key={api_key}"

            with httpx.Client(timeout=10.0) as client:
                if method == "GET":
                    response = client.get(url, headers=headers)
                else:
                    # For POST, send minimal payload
                    response = client.post(
                        url, headers=headers, json={} if method == "POST" else None
                    )

                return response.status_code in [200, 201, 204]

        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False

    def get_user_api_key(
        self,
        session: Session,
        user_id: str | uuid.UUID,
        service_name: str,
        credential_type: str | None = None,
    ) -> str | None:
        """
        Get user's API key for a service.

        Priority:
        1. User's API key (from database → Infisical)
        2. Platform default (from environment variables)
        3. None (service unavailable)

        Args:
            session: Database session
            user_id: User ID (string or UUID)
            service_name: Service name
            credential_type: Credential type

        Returns:
            API key string or None
        """
        from app.models import UserAPIKey

        # Convert user_id to string if UUID
        user_id_str = str(user_id)

        # 1. Check user's API key
        query = select(UserAPIKey).where(
            UserAPIKey.user_id == user_id_str,
            UserAPIKey.service_name == service_name,
            UserAPIKey.is_active.is_(True),
        )

        if credential_type:
            query = query.where(UserAPIKey.credential_type == credential_type)

        api_key_record = session.exec(query).first()

        if api_key_record:
            # Retrieve from Infisical
            credentials = self.retrieve_api_key(
                user_id_str, service_name, credential_type
            )
            if credentials:
                return credentials.get("api_key")

        # 2. Fallback to platform default
        from app.core.config import settings

        env_key_map = {
            # LLM Providers (actually used)
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google-ai": "GOOGLE_API_KEY",
            "cohere": "COHERE_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "replicate": "REPLICATE_API_KEY",
            # OCR Services (actually used)
            "google-vision": "GOOGLE_VISION_API_KEY",
            # Social Media (actually used)
            "twitter": "TWITTER_BEARER_TOKEN",  # Default to bearer token
            "reddit": "REDDIT_CLIENT_ID",  # Requires REDDIT_CLIENT_SECRET too
            "linkedin": "LINKEDIN_CLIENT_ID",  # Requires LINKEDIN_CLIENT_SECRET too
            # Code Execution (actually used)
            "e2b": "E2B_API_KEY",
            # Vector Databases (actually used)
            "chromadb": "CHROMA_SERVER_AUTH_TOKEN",
            "weaviate": "WEAVIATE_API_KEY",
            # Observability (actually used)
            "langsmith": "LANGSMITH_API_KEY",
            # Storage (actually used - connector manifests exist)
            "aws-s3": "AWS_ACCESS_KEY_ID",  # Requires AWS_SECRET_ACCESS_KEY too
            "azure-blob": "AZURE_STORAGE_CONNECTION_STRING",
        }

        env_key = env_key_map.get(service_name)
        if env_key:
            return getattr(settings, env_key, None) or ""

        return None

    def get_user_api_key_without_session(
        self,
        user_id: str | uuid.UUID,
        service_name: str,
        credential_type: str | None = None,
    ) -> str | None:
        """
        Get user's API key without requiring a session.

        Creates a temporary session for the lookup.
        Useful for services that don't have session context.

        Args:
            user_id: User ID (string or UUID)
            service_name: Service name
            credential_type: Credential type

        Returns:
            API key string or None
        """
        from app.core.db import engine

        with Session(engine) as session:
            return self.get_user_api_key(
                session, user_id, service_name, credential_type
            )


# Default API key service instance
default_api_key_service = APIKeyService()
