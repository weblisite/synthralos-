"""
Workflow Activity Handlers

Node execution handlers for different node types.
These will be called by the workflow engine when executing nodes.
"""

from typing import Any

from app.workflows.state import NodeExecutionResult


class ActivityError(Exception):
    """Base exception for activity errors."""

    pass


class ActivityHandler:
    """
    Base class for activity handlers.

    Activity handlers execute specific node types in workflows.
    """

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> NodeExecutionResult:
        """
        Execute an activity.

        Args:
            node_id: Node ID
            node_config: Node configuration
            input_data: Input data for the node

        Returns:
            NodeExecutionResult
        """
        raise NotImplementedError("Subclasses must implement execute()")


class TriggerActivityHandler(ActivityHandler):
    """Handler for trigger nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> NodeExecutionResult:
        """Execute trigger node."""
        # Trigger nodes typically just pass through input data
        from datetime import datetime

        return NodeExecutionResult(
            node_id=node_id,
            status="success",
            output=input_data,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=0,
        )


class HTTPRequestActivityHandler(ActivityHandler):
    """Handler for HTTP request nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> NodeExecutionResult:
        """Execute HTTP request node."""
        import json
        import time
        import urllib.parse
        import urllib.request
        from datetime import datetime

        start_time = time.time()

        try:
            # Get request configuration from node_config or input_data
            url = node_config.get("url") or input_data.get("url")
            method = node_config.get("method", "GET").upper()
            headers = node_config.get("headers", {}) or input_data.get("headers", {})
            body = node_config.get("body") or input_data.get("body")
            timeout = node_config.get("timeout", 30) or input_data.get("timeout", 30)

            if not url:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="URL is required for HTTP request",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Prepare request
            if body and isinstance(body, dict):
                body = json.dumps(body).encode("utf-8")
            elif body and isinstance(body, str):
                body = body.encode("utf-8")

            # Create request
            req = urllib.request.Request(url, data=body, method=method)

            # Add headers
            for key, value in headers.items():
                req.add_header(key, value)

            # Default Content-Type for POST/PUT/PATCH
            if method in ["POST", "PUT", "PATCH"] and "Content-Type" not in headers:
                req.add_header("Content-Type", "application/json")

            # Execute request
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    status_code = response.getcode()
                    response_headers = dict(response.headers)
                    response_body = response.read().decode("utf-8")

                    # Try to parse JSON response
                    try:
                        response_json = json.loads(response_body)
                    except json.JSONDecodeError:
                        response_json = None

                    duration_ms = int((time.time() - start_time) * 1000)

                    return NodeExecutionResult(
                        node_id=node_id,
                        status="success",
                        output={
                            "status_code": status_code,
                            "headers": response_headers,
                            "body": response_body,
                            "json": response_json,
                            "url": url,
                            "method": method,
                        },
                        started_at=datetime.utcnow(),
                        completed_at=datetime.utcnow(),
                        duration_ms=duration_ms,
                    )
            except urllib.error.HTTPError as e:
                # HTTP error (4xx, 5xx)
                response_body = e.read().decode("utf-8") if e.fp else ""
                duration_ms = int((time.time() - start_time) * 1000)

                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={
                        "status_code": e.code,
                        "headers": dict(e.headers) if e.headers else {},
                        "body": response_body,
                        "url": url,
                        "method": method,
                    },
                    error=f"HTTP {e.code}: {e.reason}",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=duration_ms,
                )
            except urllib.error.URLError as e:
                # Network error
                duration_ms = int((time.time() - start_time) * 1000)

                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={
                        "url": url,
                        "method": method,
                    },
                    error=f"Network error: {str(e)}",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=duration_ms,
                )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error=f"HTTP request failed: {str(e)}",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=duration_ms,
            )


class CodeActivityHandler(ActivityHandler):
    """Handler for code execution nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> NodeExecutionResult:
        """Execute code node."""
        from datetime import datetime

        from sqlmodel import Session

        from app.code.service import default_code_execution_service
        from app.core.db import engine

        try:
            # Get code and language from node_config or input_data
            code = node_config.get("code") or input_data.get("code")
            language = node_config.get("language", "python") or input_data.get(
                "language", "python"
            )
            runtime = node_config.get("runtime") or input_data.get(
                "runtime", "subprocess"
            )
            code_input_data = node_config.get("input_data", {}) or input_data.get(
                "input_data", {}
            )
            requirements = node_config.get("requirements", {}) or input_data.get(
                "requirements", {}
            )
            timeout_seconds = node_config.get("timeout_seconds", 30) or input_data.get(
                "timeout_seconds", 30
            )

            if not code:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="Code is required for code execution",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Use code execution service
            with Session(engine) as session:
                result = default_code_execution_service.execute_code(
                    session=session,
                    code=code,
                    language=language,
                    runtime=runtime,
                    input_data={
                        "input": code_input_data,
                        "timeout": timeout_seconds,
                    },
                    requirements=requirements,
                    timeout_seconds=timeout_seconds,
                )

            # Parse result
            if result.get("exit_code") == 0:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="success",
                    output={
                        "stdout": result.get("stdout", ""),
                        "result": result.get("result"),
                        "output_data": result.get("output_data"),
                        "memory_mb": result.get("memory_mb"),
                        "duration_ms": result.get("duration_ms", 0),
                    },
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=result.get("duration_ms", 0),
                )
            else:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={
                        "stdout": result.get("stdout", ""),
                        "stderr": result.get("stderr", ""),
                        "exit_code": result.get("exit_code"),
                        "memory_mb": result.get("memory_mb"),
                        "duration_ms": result.get("duration_ms", 0),
                    },
                    error=result.get("stderr", "Code execution failed"),
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=result.get("duration_ms", 0),
                )
        except Exception as e:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error=f"Code execution error: {str(e)}",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )


class RAGSwitchActivityHandler(ActivityHandler):
    """Handler for RAG switch nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> NodeExecutionResult:
        """
        Execute RAG switch node.

        Evaluates routing decision for RAG queries based on:
        - File size
        - Dataset size
        - Query requirements
        """
        from datetime import datetime
        from uuid import UUID

        from sqlmodel import Session

        from app.core.db import engine

        # Note: This handler doesn't have direct access to database session
        # The workflow engine should pass session if needed, or we use a service
        # For now, we'll use the RAG service which will handle session internally
        from app.rag.service import default_rag_service

        index_id_str = input_data.get("index_id") or node_config.get("index_id")
        if not index_id_str:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error="index_id is required for RAG switch",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )

        try:
            index_id = (
                UUID(index_id_str) if isinstance(index_id_str, str) else index_id_str
            )
            query_requirements = input_data.get("query_requirements", {})

            # Use RAG service to evaluate routing
            with Session(engine) as session:
                evaluation = default_rag_service.evaluate_routing(
                    session=session,
                    index_id=index_id,
                    query_requirements=query_requirements,
                )

            return NodeExecutionResult(
                node_id=node_id,
                status="success",
                output=evaluation,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )
        except Exception as e:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error=str(e),
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )


class OCRSwitchActivityHandler(ActivityHandler):
    """Handler for OCR switch nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> NodeExecutionResult:
        """
        Execute OCR switch node.

        Evaluates routing decision for OCR processing based on:
        - Layout type (table, etc.)
        - Handwriting detection
        - PDF complexity
        - Region/latency requirements
        - Structured JSON requirements

        Input:
        - document_url: Document URL or path
        - document_metadata: Optional document metadata dict
        - query_requirements: Optional query requirements dict

        Output:
        - selected_engine: Selected OCR engine
        - routing_reason: Human-readable routing reason
        - document_info: Document information
        """
        from datetime import datetime

        from app.ocr.service import default_ocr_service

        document_url = input_data.get("document_url") or node_config.get("document_url")
        if not document_url:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error="document_url is required for OCR switch",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )

        try:
            document_metadata = input_data.get("document_metadata", {})
            query_requirements = input_data.get("query_requirements", {})

            # Select OCR engine
            selected_engine = default_ocr_service.select_engine(
                document_url=document_url,
                document_metadata=document_metadata,
                query_requirements=query_requirements,
            )

            # Generate routing reason
            routing_reason = self._generate_routing_reason(
                document_url=document_url,
                document_metadata=document_metadata,
                query_requirements=query_requirements,
                selected_engine=selected_engine,
            )

            # Detect file type
            file_type = default_ocr_service._detect_file_type(document_url)

            return NodeExecutionResult(
                node_id=node_id,
                status="success",
                output={
                    "selected_engine": selected_engine,
                    "routing_reason": routing_reason,
                    "document_info": {
                        "document_url": document_url,
                        "file_type": file_type,
                        "document_metadata": document_metadata,
                    },
                    "query_requirements": query_requirements,
                },
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )
        except Exception as e:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error=str(e),
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )

    def _generate_routing_reason(
        self,
        document_url: str,
        document_metadata: dict[str, Any],
        query_requirements: dict[str, Any],
        selected_engine: str,
    ) -> str:
        """
        Generate human-readable routing reason.

        Args:
            document_url: Document URL
            document_metadata: Document metadata
            query_requirements: Query requirements
            selected_engine: Selected engine

        Returns:
            Routing reason string
        """
        reasons = []

        layout_type = query_requirements.get("layout") or document_metadata.get(
            "layout"
        )
        handwriting_detected = query_requirements.get("handwriting_detected", False)
        heavy_pdf_or_image = query_requirements.get("heavy_pdf_or_image", False)
        region = query_requirements.get("region") or document_metadata.get("region")
        latency_requirement = query_requirements.get("latency_ms", 0)
        structured_json_required = query_requirements.get(
            "structured_json_required", False
        )

        # Check requirements
        if structured_json_required:
            reasons.append("Structured JSON required → Omniparser")

        if layout_type == "table":
            reasons.append("Table layout detected → DocTR")

        if handwriting_detected:
            reasons.append("Handwriting detected → EasyOCR")

        if heavy_pdf_or_image:
            reasons.append("Heavy PDF/image → Google Vision API")

        if region == "EU" or latency_requirement > 1000:
            reasons.append("EU region or latency > 1s → PaddleOCR")

        # Default reason
        if not reasons:
            reasons.append(f"Default routing → {selected_engine}")

        return "; ".join(reasons)


# Activity handler registry
ACTIVITY_HANDLERS: dict[str, ActivityHandler] = {
    "trigger": TriggerActivityHandler(),
    "http_request": HTTPRequestActivityHandler(),
    "code": CodeActivityHandler(),
    "rag_switch": RAGSwitchActivityHandler(),
    "ocr_switch": OCRSwitchActivityHandler(),
}


def get_activity_handler(node_type: str) -> ActivityHandler | None:
    """
    Get activity handler for a node type.

    Args:
        node_type: Node type

    Returns:
        ActivityHandler instance or None
    """
    return ACTIVITY_HANDLERS.get(node_type)
