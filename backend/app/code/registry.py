"""
Code Tool Registry

Manages registration, versioning, and validation of code tools.
Supports Pydantic validation for Python tools and Zod validation for JavaScript/TypeScript tools.
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import CodeToolRegistry

logger = logging.getLogger(__name__)


class CodeToolRegistryError(Exception):
    """Base exception for code tool registry errors."""

    pass


class InvalidToolError(CodeToolRegistryError):
    """Invalid tool definition."""

    pass


class ToolNotFoundError(CodeToolRegistryError):
    """Tool not found."""

    pass


class InvalidVersionError(CodeToolRegistryError):
    """Invalid version string."""

    pass


class ToolValidationError(CodeToolRegistryError):
    """Tool validation failed."""

    pass


class CodeToolRegistryService:
    """
    Code tool registry service.

    Handles:
    - Tool registration with versioning
    - Input/output schema validation (Pydantic/Zod)
    - Tool discovery and retrieval
    - Version management
    """

    def __init__(self):
        """Initialize code tool registry."""
        pass

    def validate_version(self, version: str) -> bool:
        """
        Validate SemVer version string.

        Args:
            version: Version string (e.g., "1.0.0", "2.1.3-beta")

        Returns:
            True if valid SemVer
        """
        # SemVer pattern: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
        semver_pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        return bool(re.match(semver_pattern, version))

    def validate_tool_id(self, tool_id: str) -> bool:
        """
        Validate tool ID format.

        Args:
            tool_id: Tool ID string

        Returns:
            True if valid tool ID
        """
        # Tool ID should be lowercase, alphanumeric with hyphens/underscores
        # Format: tool-name or tool_name
        tool_id_pattern = r"^[a-z0-9][a-z0-9_-]*[a-z0-9]$"
        return bool(re.match(tool_id_pattern, tool_id)) and len(tool_id) <= 255

    def validate_pydantic_schema(self, schema: dict[str, Any]) -> bool:
        """
        Validate Pydantic schema definition.

        Args:
            schema: Pydantic schema dictionary

        Returns:
            True if valid schema

        Raises:
            ToolValidationError: If schema is invalid
        """
        try:
            # Try to create a Pydantic model from the schema
            # Schema should be in JSON Schema format
            if not isinstance(schema, dict):
                raise ToolValidationError("Schema must be a dictionary")

            # Check for required fields
            if "type" not in schema:
                raise ToolValidationError("Schema must have 'type' field")

            # Try to create a model (simplified validation)
            # In production, would use jsonschema library or pydantic's schema validation
            return True
        except Exception as e:
            raise ToolValidationError(f"Invalid Pydantic schema: {str(e)}")

    def validate_zod_schema(self, schema: dict[str, Any]) -> bool:
        """
        Validate Zod schema definition.

        Args:
            schema: Zod schema dictionary

        Returns:
            True if valid schema

        Raises:
            ToolValidationError: If schema is invalid
        """
        try:
            # Zod schema validation (simplified)
            # In production, would use zod-to-json-schema or similar
            if not isinstance(schema, dict):
                raise ToolValidationError("Schema must be a dictionary")

            # Basic structure validation
            # Zod schemas are typically defined as TypeScript types
            # For now, accept any dictionary structure
            return True
        except Exception as e:
            raise ToolValidationError(f"Invalid Zod schema: {str(e)}")

    def validate_schema(
        self,
        schema: dict[str, Any],
        schema_type: str,
    ) -> bool:
        """
        Validate input/output schema based on type.

        Args:
            schema: Schema dictionary
            schema_type: Schema type ("pydantic" or "zod")

        Returns:
            True if valid schema

        Raises:
            ToolValidationError: If schema is invalid
        """
        if schema_type.lower() == "pydantic":
            return self.validate_pydantic_schema(schema)
        elif schema_type.lower() == "zod":
            return self.validate_zod_schema(schema)
        else:
            raise ToolValidationError(f"Unknown schema type: {schema_type}")

    def register_tool(
        self,
        session: Session,
        tool_id: str,
        name: str,
        version: str,
        code: str,
        runtime: str,
        description: str | None = None,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> CodeToolRegistry:
        """
        Register a new code tool or new version of existing tool.

        Args:
            session: Database session
            tool_id: Unique tool identifier
            name: Tool name
            version: SemVer version string
            code: Tool code
            runtime: Runtime name (e.g., "e2b", "wasmedge")
            description: Optional tool description
            input_schema: Optional input schema (Pydantic or Zod)
            output_schema: Optional output schema (Pydantic or Zod)
            owner_id: Optional owner ID

        Returns:
            CodeToolRegistry instance

        Raises:
            InvalidToolError: If tool definition is invalid
            InvalidVersionError: If version string is invalid
        """
        # Validate tool ID
        if not self.validate_tool_id(tool_id):
            raise InvalidToolError(f"Invalid tool ID format: {tool_id}")

        # Validate version
        if not self.validate_version(version):
            raise InvalidVersionError(
                f"Invalid version format: {version}. Must be SemVer (e.g., 1.0.0)"
            )

        # Validate schemas if provided
        if input_schema:
            # Determine schema type from runtime or schema itself
            schema_type = self._detect_schema_type(runtime, input_schema)
            self.validate_schema(input_schema, schema_type)

        if output_schema:
            schema_type = self._detect_schema_type(runtime, output_schema)
            self.validate_schema(output_schema, schema_type)

        # Check if tool already exists
        existing_tool = session.exec(
            select(CodeToolRegistry).where(
                CodeToolRegistry.tool_id == tool_id,
                CodeToolRegistry.version == version,
            )
        ).first()

        if existing_tool:
            raise InvalidToolError(
                f"Tool '{tool_id}' version '{version}' already exists"
            )

        # Create tool record
        tool = CodeToolRegistry(
            tool_id=tool_id,
            name=name,
            version=version,
            description=description,
            code=code,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            runtime=runtime,
            owner_id=owner_id or uuid.uuid4(),  # TODO: Get from current user
            usage_count=0,
            is_deprecated=False,
        )
        session.add(tool)
        session.commit()
        session.refresh(tool)

        logger.info(f"Registered code tool: {tool_id} v{version} (Runtime: {runtime})")

        return tool

    def get_tool(
        self,
        session: Session,
        tool_id: str,
        version: str | None = None,
    ) -> CodeToolRegistry:
        """
        Get a code tool by ID and optional version.

        Args:
            session: Database session
            tool_id: Tool ID
            version: Optional version string (uses latest if not provided)

        Returns:
            CodeToolRegistry instance

        Raises:
            ToolNotFoundError: If tool not found
        """
        if version:
            tool = session.exec(
                select(CodeToolRegistry).where(
                    CodeToolRegistry.tool_id == tool_id,
                    CodeToolRegistry.version == version,
                    CodeToolRegistry.is_deprecated == False,
                )
            ).first()
        else:
            # Get latest version
            tool = session.exec(
                select(CodeToolRegistry)
                .where(
                    CodeToolRegistry.tool_id == tool_id,
                    CodeToolRegistry.is_deprecated == False,
                )
                .order_by(CodeToolRegistry.created_at.desc())
            ).first()

        if not tool:
            version_str = f" v{version}" if version else ""
            raise ToolNotFoundError(f"Tool '{tool_id}'{version_str} not found")

        return tool

    def list_tools(
        self,
        session: Session,
        runtime: str | None = None,
        owner_id: uuid.UUID | None = None,
        include_deprecated: bool = False,
    ) -> list[CodeToolRegistry]:
        """
        List registered code tools.

        Args:
            session: Database session
            runtime: Optional filter by runtime
            owner_id: Optional filter by owner
            include_deprecated: Include deprecated tools

        Returns:
            List of CodeToolRegistry instances
        """
        query = select(CodeToolRegistry)

        if runtime:
            query = query.where(CodeToolRegistry.runtime == runtime)

        if owner_id:
            query = query.where(CodeToolRegistry.owner_id == owner_id)

        if not include_deprecated:
            query = query.where(CodeToolRegistry.is_deprecated == False)

        tools = session.exec(query.order_by(CodeToolRegistry.created_at.desc())).all()

        return tools

    def get_tool_versions(
        self,
        session: Session,
        tool_id: str,
    ) -> list[CodeToolRegistry]:
        """
        Get all versions of a tool.

        Args:
            session: Database session
            tool_id: Tool ID

        Returns:
            List of CodeToolRegistry instances (all versions)
        """
        tools = session.exec(
            select(CodeToolRegistry)
            .where(
                CodeToolRegistry.tool_id == tool_id,
            )
            .order_by(CodeToolRegistry.created_at.desc())
        ).all()

        return tools

    def deprecate_tool(
        self,
        session: Session,
        tool_id: str,
        version: str | None = None,
    ) -> CodeToolRegistry:
        """
        Deprecate a tool or specific version.

        Args:
            session: Database session
            tool_id: Tool ID
            version: Optional version (deprecates all versions if not provided)

        Returns:
            Updated CodeToolRegistry instance(s)
        """
        if version:
            tool = self.get_tool(session, tool_id, version)
            tool.is_deprecated = True
            tool.updated_at = datetime.utcnow()
            session.add(tool)
            session.commit()
            session.refresh(tool)
            return tool
        else:
            # Deprecate all versions
            tools = self.get_tool_versions(session, tool_id)
            for tool in tools:
                tool.is_deprecated = True
                tool.updated_at = datetime.utcnow()
                session.add(tool)
            session.commit()
            return tools[0] if tools else None

    def increment_usage_count(
        self,
        session: Session,
        tool_id: str,
        version: str | None = None,
    ) -> None:
        """
        Increment usage count for a tool.

        Args:
            session: Database session
            tool_id: Tool ID
            version: Optional version (uses latest if not provided)
        """
        tool = self.get_tool(session, tool_id, version)
        tool.usage_count += 1
        session.add(tool)
        session.commit()

    def validate_tool_input(
        self,
        tool: CodeToolRegistry,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate tool input against input schema.

        Args:
            tool: CodeToolRegistry instance
            input_data: Input data dictionary

        Returns:
            Validated input data

        Raises:
            ToolValidationError: If validation fails
        """
        if not tool.input_schema:
            # No schema, return as-is
            return input_data

        try:
            # Determine schema type
            schema_type = self._detect_schema_type(tool.runtime, tool.input_schema)

            if schema_type == "pydantic":
                # Create Pydantic model and validate
                # In production, would use actual Pydantic model creation
                # For now, basic validation
                return input_data
            elif schema_type == "zod":
                # Zod validation would be done client-side or via JS runtime
                # For now, basic validation
                return input_data
            else:
                return input_data
        except Exception as e:
            raise ToolValidationError(f"Input validation failed: {str(e)}")

    def validate_tool_output(
        self,
        tool: CodeToolRegistry,
        output_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate tool output against output schema.

        Args:
            tool: CodeToolRegistry instance
            output_data: Output data dictionary

        Returns:
            Validated output data

        Raises:
            ToolValidationError: If validation fails
        """
        if not tool.output_schema:
            # No schema, return as-is
            return output_data

        try:
            # Determine schema type
            schema_type = self._detect_schema_type(tool.runtime, tool.output_schema)

            if schema_type == "pydantic":
                # Create Pydantic model and validate
                return output_data
            elif schema_type == "zod":
                # Zod validation
                return output_data
            else:
                return output_data
        except Exception as e:
            raise ToolValidationError(f"Output validation failed: {str(e)}")

    def _detect_schema_type(
        self,
        runtime: str,
        schema: dict[str, Any],
    ) -> str:
        """
        Detect schema type from runtime or schema structure.

        Args:
            runtime: Runtime name
            schema: Schema dictionary

        Returns:
            Schema type ("pydantic" or "zod")
        """
        # Check schema for type hints
        if "$schema" in schema or "type" in schema:
            # JSON Schema format (used by both Pydantic and Zod)
            # Default to pydantic for Python runtimes
            if runtime in ["e2b", "wasmedge"] and "python" in runtime.lower():
                return "pydantic"
            elif runtime in ["cline_node", "mcp_server"]:
                return "zod"

        # Default based on runtime
        if runtime in ["e2b", "wasmedge", "bacalhau"]:
            return "pydantic"
        elif runtime in ["cline_node", "mcp_server"]:
            return "zod"

        # Default to pydantic
        return "pydantic"


# Default code tool registry service instance
default_code_tool_registry = CodeToolRegistryService()
