"""
Guardrails Dependencies

Dependencies for input validation and guardrails.
"""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

from app.guardrails.service import default_guardrails_service


def validate_input(
    data: dict[str, Any],
    schema: dict[str, Any] | type[BaseModel] | None = None,
    validator_type: str = "pydantic",
) -> dict[str, Any]:
    """
    Validate input data using guardrails.
    
    Args:
        data: Input data to validate
        schema: Optional validation schema
        validator_type: "pydantic" or "zod"
        
    Returns:
        Validated data
        
    Raises:
        HTTPException: If validation fails
    """
    guardrails = default_guardrails_service
    
    is_valid, validated_data, error_message = guardrails.validate_input(
        data=data,
        schema=schema,
        validator_type=validator_type,
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message or "Input validation failed",
        )
    
    return validated_data or data


def check_abuse(
    content: str,
    user_id: str | None = None,
) -> None:
    """
    Check for abuse patterns in content.
    
    Args:
        content: Content to check
        user_id: Optional user ID
        
    Raises:
        HTTPException: If abuse detected
    """
    guardrails = default_guardrails_service
    
    is_safe, reason = guardrails.check_abuse(
        content=content,
        user_id=user_id,
    )
    
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request blocked: {reason}",
        )


def filter_content(
    content: str,
    filter_type: str = "basic",
) -> str:
    """
    Filter potentially harmful content.
    
    Args:
        content: Content to filter
        filter_type: Type of filtering ("basic", "strict", "custom")
        
    Returns:
        Filtered content
    """
    guardrails = default_guardrails_service
    
    filtered_content, _ = guardrails.filter_content(
        content=content,
        filter_type=filter_type,
    )
    
    return filtered_content

