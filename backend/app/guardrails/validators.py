"""
Input Validators

Pydantic and Zod validation for input sanitization and validation.
"""

import json
import logging
from typing import Any

from pydantic import BaseModel, ValidationError as PydanticValidationError

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Base exception for validation errors."""
    pass


class PydanticValidator:
    """
    Pydantic-based validator for Python input validation.
    
    Uses Pydantic models to validate and sanitize input data.
    """
    
    def __init__(self):
        """Initialize Pydantic validator."""
        pass
    
    def validate(
        self,
        data: dict[str, Any],
        schema: dict[str, Any] | type[BaseModel],
    ) -> tuple[bool, dict[str, Any] | None, str | None]:
        """
        Validate data against a Pydantic schema.
        
        Args:
            data: Data to validate
            schema: Pydantic model class or schema dictionary
            
        Returns:
            Tuple of (is_valid, validated_data, error_message)
        """
        try:
            if isinstance(schema, dict):
                # Create a dynamic Pydantic model from schema dict
                model = self._create_model_from_schema(schema)
            else:
                # Use provided Pydantic model class
                model = schema
            
            # Validate and parse data
            validated = model(**data)
            
            # Convert to dict
            validated_data = validated.model_dump()
            
            return True, validated_data, None
            
        except PydanticValidationError as e:
            error_msg = "; ".join([f"{err['loc']}: {err['msg']}" for err in e.errors()])
            return False, None, f"Validation failed: {error_msg}"
        except Exception as e:
            logger.error(f"Pydantic validation error: {e}")
            return False, None, f"Validation error: {str(e)}"
    
    def _create_model_from_schema(self, schema: dict[str, Any]) -> type[BaseModel]:
        """
        Create a Pydantic model from a schema dictionary.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            Pydantic model class
        """
        # Simple implementation - can be enhanced with proper type conversion
        fields = {}
        for field_name, field_type in schema.items():
            # Default to str if type not specified
            if isinstance(field_type, type):
                fields[field_name] = (field_type, ...)
            else:
                fields[field_name] = (str, ...)
        
        return type("DynamicModel", (BaseModel,), fields)
    
    def sanitize(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize input data by removing potentially dangerous fields.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        sanitized = {}
        dangerous_keys = ["__class__", "__dict__", "__module__", "__builtins__"]
        
        for key, value in data.items():
            if key not in dangerous_keys:
                if isinstance(value, dict):
                    sanitized[key] = self.sanitize(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        self.sanitize(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    sanitized[key] = value
        
        return sanitized


class ZodValidator:
    """
    Zod-based validator for JavaScript/TypeScript input validation.
    
    Uses Zod schemas (via JSON Schema conversion) to validate input data.
    """
    
    def __init__(self):
        """Initialize Zod validator."""
        pass
    
    def validate(
        self,
        data: dict[str, Any],
        schema: dict[str, Any],
    ) -> tuple[bool, dict[str, Any] | None, str | None]:
        """
        Validate data against a Zod schema (converted to JSON Schema).
        
        Args:
            data: Data to validate
            schema: Zod schema as JSON Schema
            
        Returns:
            Tuple of (is_valid, validated_data, error_message)
        """
        try:
            # Convert Zod schema to JSON Schema format
            json_schema = self._zod_to_json_schema(schema)
            
            # Use jsonschema library for validation
            # Note: This is a simplified implementation
            # Full Zod validation would require a JavaScript runtime
            
            # Basic validation
            validated_data = self._validate_against_json_schema(data, json_schema)
            
            return True, validated_data, None
            
        except Exception as e:
            logger.error(f"Zod validation error: {e}")
            return False, None, f"Validation error: {str(e)}"
    
    def _zod_to_json_schema(self, zod_schema: dict[str, Any]) -> dict[str, Any]:
        """
        Convert Zod schema to JSON Schema format.
        
        Args:
            zod_schema: Zod schema dictionary
            
        Returns:
            JSON Schema dictionary
        """
        # Simplified conversion - full implementation would handle all Zod types
        json_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        
        for field_name, field_def in zod_schema.items():
            if isinstance(field_def, dict):
                field_type = field_def.get("type", "string")
                json_schema["properties"][field_name] = {"type": field_type}
                
                if field_def.get("required", False):
                    json_schema["required"].append(field_name)
        
        return json_schema
    
    def _validate_against_json_schema(
        self,
        data: dict[str, Any],
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate data against JSON Schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema
            
        Returns:
            Validated data
        """
        # Basic validation - can be enhanced with jsonschema library
        validated = {}
        
        for field_name, field_value in data.items():
            if field_name in schema.get("properties", {}):
                field_schema = schema["properties"][field_name]
                field_type = field_schema.get("type", "string")
                
                # Type checking
                if field_type == "string" and isinstance(field_value, str):
                    validated[field_name] = field_value
                elif field_type == "number" and isinstance(field_value, (int, float)):
                    validated[field_name] = field_value
                elif field_type == "boolean" and isinstance(field_value, bool):
                    validated[field_name] = field_value
                elif field_type == "object" and isinstance(field_value, dict):
                    validated[field_name] = field_value
                elif field_type == "array" and isinstance(field_value, list):
                    validated[field_name] = field_value
        
        return validated
    
    def sanitize(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize input data by removing potentially dangerous fields.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        sanitized = {}
        dangerous_keys = ["__class__", "__dict__", "__module__", "__builtins__"]
        
        for key, value in data.items():
            if key not in dangerous_keys:
                if isinstance(value, dict):
                    sanitized[key] = self.sanitize(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        self.sanitize(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    sanitized[key] = value
        
        return sanitized

