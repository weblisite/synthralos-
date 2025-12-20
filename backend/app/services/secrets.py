"""
Infisical Secrets Service

Manages secrets storage and retrieval using Infisical.
Provides runtime secret injection for connectors and workflows.
"""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class SecretsServiceError(Exception):
    """Base exception for secrets service errors."""

    pass


class SecretNotFoundError(SecretsServiceError):
    """Secret not found."""

    pass


class SecretsService:
    """
    Secrets management service using Infisical.

    Provides:
    - Secret storage (encrypted in Infisical)
    - Runtime secret retrieval
    - Secret rotation support
    - Audit logging
    """

    def __init__(self):
        """Initialize secrets service."""
        self.infisical_url = settings.INFISICAL_URL
        self.client_id = settings.INFISICAL_CLIENT_ID
        self.client_secret = settings.INFISICAL_CLIENT_SECRET
        self._client = None
        self._cache: dict[str, Any] = {}  # In-memory cache for secrets

    @property
    def client(self):
        """Get Infisical client (lazy initialization)."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self):
        """Create Infisical client."""
        if not self.infisical_url or not self.client_id or not self.client_secret:
            logger.warning(
                "Infisical credentials not configured. Secrets service will use mock mode."
            )
            return None

        try:
            # Try to import Infisical SDK
            # Note: Infisical SDK may have pydantic version conflicts
            # For now, we'll use HTTP requests directly if SDK unavailable
            try:
                from infisical import InfisicalClient

                client = InfisicalClient(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    site_url=self.infisical_url,
                )
                logger.info("Infisical client initialized successfully")
                return client
            except ImportError:
                # Fallback to HTTP-based implementation
                logger.info("Infisical SDK not available, using HTTP client")
                return self._create_http_client()
        except Exception as e:
            logger.error(f"Failed to initialize Infisical client: {e}")
            return None

    def _create_http_client(self):
        """Create HTTP-based Infisical client."""
        # Return a simple object that implements the same interface
        # This allows the service to work without the SDK
        return type(
            "HTTPClient",
            (),
            {
                "create_secret": self._http_create_secret,
                "get_secret": self._http_get_secret,
                "delete_secret": self._http_delete_secret,
            },
        )()

    def _http_create_secret(
        self, secret_name: str, secret_value: str, environment: str, path: str
    ):
        """HTTP-based secret creation."""
        # TODO: Implement HTTP-based Infisical API calls
        logger.warning("HTTP-based Infisical client not fully implemented")
        pass

    def _http_get_secret(self, secret_name: str, environment: str, path: str):
        """HTTP-based secret retrieval."""
        # TODO: Implement HTTP-based Infisical API calls
        logger.warning("HTTP-based Infisical client not fully implemented")
        return None

    def _http_delete_secret(self, secret_name: str, environment: str, path: str):
        """HTTP-based secret deletion."""
        # TODO: Implement HTTP-based Infisical API calls
        logger.warning("HTTP-based Infisical client not fully implemented")
        pass

    def store_secret(
        self,
        secret_key: str,
        secret_value: str,
        environment: str = "dev",
        project_id: str | None = None,
        path: str = "/",
    ) -> None:
        """
        Store a secret in Infisical.

        Args:
            secret_key: Secret key/name
            secret_value: Secret value
            environment: Environment (dev, staging, prod)
            project_id: Project ID (optional, uses default if None)
            path: Secret path in Infisical
        """
        if not self.client:
            logger.warning(f"Infisical not available, secret '{secret_key}' not stored")
            return

        try:
            # Store secret via Infisical API
            # Note: Actual implementation depends on Infisical SDK API
            self.client.create_secret(
                secret_name=secret_key,
                secret_value=secret_value,
                environment=environment,
                path=path,
            )

            # Clear cache for this key
            cache_key = f"{project_id or 'default'}:{environment}:{path}:{secret_key}"
            self._cache.pop(cache_key, None)

            logger.info(f"Secret stored: {secret_key} (environment: {environment})")
        except Exception as e:
            logger.error(f"Failed to store secret '{secret_key}': {e}")
            raise SecretsServiceError(f"Failed to store secret: {e}")

    def get_secret(
        self,
        secret_key: str,
        environment: str = "dev",
        project_id: str | None = None,
        path: str = "/",
        use_cache: bool = True,
    ) -> str:
        """
        Get a secret from Infisical.

        Args:
            secret_key: Secret key/name
            environment: Environment (dev, staging, prod)
            project_id: Project ID (optional)
            path: Secret path in Infisical

        Returns:
            Secret value

        Raises:
            SecretNotFoundError: If secret not found
        """
        cache_key = f"{project_id or 'default'}:{environment}:{path}:{secret_key}"

        # Check cache first
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        if not self.client:
            logger.warning(
                f"Infisical not available, returning empty string for '{secret_key}'"
            )
            return ""

        try:
            # Get secret via Infisical API
            secret = self.client.get_secret(
                secret_name=secret_key,
                environment=environment,
                path=path,
            )

            if not secret:
                raise SecretNotFoundError(f"Secret '{secret_key}' not found")

            secret_value = (
                secret.secret_value if hasattr(secret, "secret_value") else str(secret)
            )

            # Cache the secret
            if use_cache:
                self._cache[cache_key] = secret_value

            logger.debug(f"Secret retrieved: {secret_key} (environment: {environment})")
            return secret_value

        except SecretNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get secret '{secret_key}': {e}")
            raise SecretsServiceError(f"Failed to get secret: {e}")

    def get_secrets(
        self,
        secret_keys: list[str],
        environment: str = "dev",
        project_id: str | None = None,
        path: str = "/",
    ) -> dict[str, str]:
        """
        Get multiple secrets at once.

        Args:
            secret_keys: List of secret keys
            environment: Environment
            project_id: Project ID
            path: Secret path

        Returns:
            Dictionary of secret_key -> secret_value
        """
        secrets = {}
        for key in secret_keys:
            try:
                secrets[key] = self.get_secret(
                    key,
                    environment=environment,
                    project_id=project_id,
                    path=path,
                )
            except SecretNotFoundError:
                logger.warning(f"Secret '{key}' not found, skipping")
                secrets[key] = None

        return secrets

    def delete_secret(
        self,
        secret_key: str,
        environment: str = "dev",
        project_id: str | None = None,
        path: str = "/",
    ) -> None:
        """
        Delete a secret from Infisical.

        Args:
            secret_key: Secret key/name
            environment: Environment
            project_id: Project ID
            path: Secret path
        """
        if not self.client:
            logger.warning(
                f"Infisical not available, secret '{secret_key}' not deleted"
            )
            return

        try:
            self.client.delete_secret(
                secret_name=secret_key,
                environment=environment,
                path=path,
            )

            # Clear cache
            cache_key = f"{project_id or 'default'}:{environment}:{path}:{secret_key}"
            self._cache.pop(cache_key, None)

            logger.info(f"Secret deleted: {secret_key} (environment: {environment})")
        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_key}': {e}")
            raise SecretsServiceError(f"Failed to delete secret: {e}")

    def rotate_secret(
        self,
        secret_key: str,
        new_secret_value: str,
        environment: str = "dev",
        project_id: str | None = None,
        path: str = "/",
    ) -> None:
        """
        Rotate a secret (update with new value).

        Args:
            secret_key: Secret key/name
            new_secret_value: New secret value
            environment: Environment
            project_id: Project ID
            path: Secret path
        """
        self.store_secret(
            secret_key=secret_key,
            secret_value=new_secret_value,
            environment=environment,
            project_id=project_id,
            path=path,
        )
        logger.info(f"Secret rotated: {secret_key} (environment: {environment})")

    def inject_secrets(
        self,
        config: dict[str, Any],
        secret_keys: list[str],
        environment: str = "dev",
        project_id: str | None = None,
        path: str = "/",
    ) -> dict[str, Any]:
        """
        Inject secrets into a configuration dictionary.

        Replaces placeholder values (e.g., "${SECRET_KEY}") with actual secret values.

        Args:
            config: Configuration dictionary
            secret_keys: List of secret keys to inject
            environment: Environment
            project_id: Project ID
            path: Secret path

        Returns:
            Configuration dictionary with secrets injected
        """
        secrets = self.get_secrets(
            secret_keys=secret_keys,
            environment=environment,
            project_id=project_id,
            path=path,
        )

        # Create a copy of config
        injected_config = config.copy()

        # Replace placeholders with secret values
        for key, value in secrets.items():
            placeholder = f"${{{key}}}"
            # Recursively replace in nested dicts
            injected_config = self._replace_placeholders(
                injected_config,
                placeholder,
                value,
            )

        return injected_config

    def _replace_placeholders(
        self,
        obj: Any,
        placeholder: str,
        replacement: str,
    ) -> Any:
        """Recursively replace placeholders in nested structures."""
        if isinstance(obj, dict):
            return {
                k: self._replace_placeholders(v, placeholder, replacement)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [
                self._replace_placeholders(item, placeholder, replacement)
                for item in obj
            ]
        elif isinstance(obj, str):
            return obj.replace(placeholder, replacement)
        else:
            return obj

    def clear_cache(self) -> None:
        """Clear the secrets cache."""
        self._cache.clear()
        logger.debug("Secrets cache cleared")


# Default secrets service instance
default_secrets_service = SecretsService()
