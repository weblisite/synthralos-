"""
Guardrails Middleware

Middleware for automatic input validation and abuse detection.
"""

import logging
from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.guardrails.service import default_guardrails_service

logger = logging.getLogger(__name__)


class GuardrailsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic input validation and abuse detection.
    
    Applies guardrails to:
    - Request body validation
    - Query parameter validation
    - Abuse pattern detection
    """
    
    def __init__(self, app, enable_validation: bool = True, enable_abuse_check: bool = True):
        """
        Initialize guardrails middleware.
        
        Args:
            app: Application instance
            enable_validation: Enable input validation
            enable_abuse_check: Enable abuse detection
        """
        super().__init__(app)
        self.guardrails = default_guardrails_service
        self.enable_validation = enable_validation
        self.enable_abuse_check = enable_abuse_check
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through guardrails.
        
        Args:
            request: HTTP request
            call_next: Next middleware handler
            
        Returns:
            Response
        """
        # Skip guardrails for certain paths
        skip_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Check for abuse patterns in URL and headers
        if self.enable_abuse_check:
            url_content = str(request.url)
            headers_content = str(request.headers)
            
            is_safe, reason = self.guardrails.check_abuse(
                f"{url_content} {headers_content}",
                user_id=None,
            )
            
            if not is_safe:
                logger.warning(f"Abuse detected in request: {reason}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Request blocked: {reason}",
                )
        
        # Validate request body if present
        if self.enable_validation and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Read body
                body = await request.body()
                
                if body:
                    import json
                    try:
                        body_data = json.loads(body)
                        
                        # Sanitize input
                        sanitized_data = self.guardrails.sanitize_input(body_data)
                        
                        # Replace request body with sanitized data
                        # Note: This requires creating a new request
                        # For now, we'll just validate and log
                        if sanitized_data != body_data:
                            logger.info("Request body was sanitized")
                    
                    except json.JSONDecodeError:
                        # Not JSON, check as string
                        body_str = body.decode("utf-8")
                        is_safe, reason = self.guardrails.check_abuse(body_str)
                        
                        if not is_safe:
                            logger.warning(f"Abuse detected in request body: {reason}")
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Request blocked: {reason}",
                            )
            
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Guardrails validation error: {e}")
                # Don't block request on validation errors, just log
        
        # Process request
        response = await call_next(request)
        
        return response

