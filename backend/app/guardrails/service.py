"""
Guardrails Service

Main service for input validation, content filtering, and abuse detection.
Integrates Pydantic/Zod validation, GuardrailsAI, and ArchGW abuse router.
"""

import logging
from typing import Any

from app.guardrails.validators import PydanticValidator, ZodValidator

logger = logging.getLogger(__name__)


class GuardrailsServiceError(Exception):
    """Base exception for guardrails service errors."""

    pass


class GuardrailsService:
    """
    Guardrails service for input validation and abuse detection.

    Provides:
    - Pydantic/Zod validation
    - GuardrailsAI integration
    - ArchGW abuse router
    - Content filtering
    """

    def __init__(self):
        """Initialize guardrails service."""
        self.pydantic_validator = PydanticValidator()
        self.zod_validator = ZodValidator()
        self._guardrailsai_available = False
        self._archgw_available = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check availability of external guardrails services."""
        try:
            import guardrails as gr

            self._guardrailsai_available = True
            logger.info("GuardrailsAI is available")
        except ImportError:
            logger.warning(
                "GuardrailsAI is not installed. Install with: pip install guardrails-ai"
            )
            self._guardrailsai_available = False

        try:
            # ArchGW integration check
            # Note: ArchGW may be a custom service or library
            # self._archgw_available = True
            self._archgw_available = False  # Placeholder
            logger.info("ArchGW abuse router check completed")
        except Exception as e:
            logger.warning(f"ArchGW not available: {e}")
            self._archgw_available = False

    def validate_input(
        self,
        data: dict[str, Any],
        schema: dict[str, Any] | None = None,
        validator_type: str = "pydantic",
    ) -> tuple[bool, dict[str, Any] | None, str | None]:
        """
        Validate input data using Pydantic or Zod validator.

        Args:
            data: Input data to validate
            schema: Optional validation schema
            validator_type: "pydantic" or "zod"

        Returns:
            Tuple of (is_valid, validated_data, error_message)
        """
        # Sanitize input first
        sanitized_data = self.sanitize_input(data)

        if not schema:
            # No schema provided, just sanitize
            return True, sanitized_data, None

        # Validate against schema
        if validator_type == "pydantic":
            return self.pydantic_validator.validate(sanitized_data, schema)
        elif validator_type == "zod":
            return self.zod_validator.validate(sanitized_data, schema)
        else:
            return False, None, f"Unknown validator type: {validator_type}"

    def sanitize_input(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize input data by removing dangerous fields.

        Args:
            data: Input data to sanitize

        Returns:
            Sanitized data
        """
        return self.pydantic_validator.sanitize(data)

    def check_abuse(
        self,
        content: str,
        user_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> tuple[bool, str | None]:
        """
        Check for abuse patterns using ArchGW abuse router.

        Args:
            content: Content to check
            user_id: Optional user ID
            context: Optional context data

        Returns:
            Tuple of (is_safe, reason)
        """
        if not self._archgw_available:
            # Fallback to basic checks
            return self._basic_abuse_check(content)

        try:
            # ArchGW abuse detection
            # Placeholder implementation
            # Replace with actual ArchGW API calls when available
            return self._basic_abuse_check(content)

        except Exception as e:
            logger.error(f"Abuse check failed: {e}")
            # Fail open for now, but log the error
            return True, None

    def _basic_abuse_check(self, content: str) -> tuple[bool, str | None]:
        """
        Basic abuse pattern detection.

        Args:
            content: Content to check

        Returns:
            Tuple of (is_safe, reason)
        """
        # Basic patterns to detect
        dangerous_patterns = [
            ("<script", "Potential XSS attack"),
            ("javascript:", "Potential XSS attack"),
            ("onerror=", "Potential XSS attack"),
            ("onload=", "Potential XSS attack"),
            ("eval(", "Potential code injection"),
            ("exec(", "Potential code injection"),
            ("__import__", "Potential code injection"),
        ]

        content_lower = content.lower()

        for pattern, reason in dangerous_patterns:
            if pattern.lower() in content_lower:
                return False, reason

        return True, None

    def validate_with_guardrailsai(
        self,
        content: str,
        schema: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any] | None, str | None]:
        """
        Validate content using GuardrailsAI.

        Args:
            content: Content to validate
            schema: Optional GuardrailsAI schema

        Returns:
            Tuple of (is_valid, validated_data, error_message)
        """
        if not self._guardrailsai_available:
            return False, None, "GuardrailsAI is not available"

        try:
            import guardrails as gr

            # Create Guardrails validator
            if schema:
                guard = gr.Guard.from_pydantic(schema)
            else:
                # Use default guard
                guard = gr.Guard()

            # Validate content
            result = guard.validate(content)

            return True, result, None

        except Exception as e:
            logger.error(f"GuardrailsAI validation failed: {e}")
            return False, None, f"GuardrailsAI validation error: {str(e)}"

    def filter_content(
        self,
        content: str,
        filter_type: str = "basic",
    ) -> tuple[str, bool]:
        """
        Filter potentially harmful content.

        Args:
            content: Content to filter
            filter_type: Type of filtering ("basic", "strict", "custom")

        Returns:
            Tuple of (filtered_content, was_filtered)
        """
        filtered = content
        was_filtered = False

        # Basic filtering
        if filter_type == "basic":
            # Remove common dangerous patterns
            dangerous_patterns = [
                "<script",
                "javascript:",
                "onerror=",
                "onload=",
            ]

            for pattern in dangerous_patterns:
                if pattern.lower() in filtered.lower():
                    filtered = filtered.replace(pattern, "")
                    was_filtered = True

        # Strict filtering
        elif filter_type == "strict":
            # More aggressive filtering
            import re

            # Remove script tags
            filtered = re.sub(
                r"<script[^>]*>.*?</script>",
                "",
                filtered,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if filtered != content:
                was_filtered = True

            # Remove event handlers
            filtered = re.sub(r"on\w+\s*=", "", filtered, flags=re.IGNORECASE)
            if filtered != content:
                was_filtered = True

        return filtered, was_filtered


# Default guardrails service instance
default_guardrails_service = GuardrailsService()
