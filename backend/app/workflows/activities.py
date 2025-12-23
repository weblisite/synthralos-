"""
Workflow Activity Handlers

Node execution handlers for different node types.
These will be called by the workflow engine when executing nodes.
"""

from typing import Any
from uuid import UUID

from sqlmodel import Session

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
        execution_id: UUID | None = None,
        session: Session | None = None,
    ) -> NodeExecutionResult:
        """
        Execute an activity.

        Args:
            node_id: Node ID
            node_config: Node configuration
            input_data: Input data for the node
            execution_id: Optional execution ID (for handlers that need it)
            session: Optional database session (for handlers that need it)

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
        execution_id: UUID | None = None,
        session: Session | None = None,
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
        execution_id: UUID | None = None,
        session: Session | None = None,
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
        execution_id: UUID | None = None,
        session: Session | None = None,
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
        execution_id: UUID | None = None,
        session: Session | None = None,
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
        execution_id: UUID | None = None,
        session: Session | None = None,
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


class ConnectorActivityHandler(ActivityHandler):
    """Handler for connector nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
        execution_id: UUID | None = None,
        session: Session | None = None,
    ) -> NodeExecutionResult:
        """Execute connector node."""
        from datetime import datetime

        if not session:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error="Database session required for connector execution",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )

        try:
            from app.connectors.loader import default_connector_loader
            from app.connectors.oauth import default_oauth_service
            from app.connectors.registry import default_connector_registry
            from app.models import Workflow, WorkflowExecution

            # Get connector slug and action from node config
            connector_slug = node_config.get("connector_slug") or node_config.get(
                "connector_id"
            )
            action = node_config.get("action") or node_config.get("action_id")

            if not connector_slug:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="connector_slug is required for connector node",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            if not action:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="action is required for connector node",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Get user_id from execution -> workflow -> owner_id
            user_id = None
            if execution_id:
                execution = session.get(WorkflowExecution, execution_id)
                if execution:
                    workflow = session.get(Workflow, execution.workflow_id)
                    if workflow:
                        user_id = workflow.owner_id

            if not user_id:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="Could not determine user_id from execution context",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Get connector version
            connector_version = default_connector_registry.get_connector(
                session=session, slug=connector_slug
            )

            # Get OAuth tokens if connector requires OAuth
            credentials = None
            manifest = connector_version.manifest
            oauth_config = manifest.get("oauth", {})

            if oauth_config:
                tokens = default_oauth_service.get_tokens(
                    connector_slug=connector_slug, user_id=user_id
                )

                if tokens:
                    credentials = {
                        "access_token": tokens.get("access_token"),
                        "refresh_token": tokens.get("refresh_token"),
                        "token_type": tokens.get("token_type", "Bearer"),
                    }

                    # Add additional credential fields from manifest
                    credential_fields = oauth_config.get("credential_fields", {})
                    for field_name, field_config in credential_fields.items():
                        if field_config.get("source") == "infisical":
                            secret_key = field_config.get(
                                "secret_key",
                                f"connector_{connector_slug}_user_{user_id}_{field_name}",
                            )
                            try:
                                from app.services.secrets import (
                                    default_secrets_service,
                                )

                                value = default_secrets_service.get_secret(
                                    secret_key=secret_key,
                                    environment="prod",
                                    path=f"/connectors/{connector_slug}/users/{user_id}",
                                )
                                credentials[field_name] = value
                            except Exception:
                                pass

            # Prepare input data (merge node_config and input_data)
            action_input = {**input_data}
            if "input_data" in node_config:
                action_input.update(node_config["input_data"])

            # Invoke connector action
            result = default_connector_loader.invoke_action(
                connector_version=connector_version,
                action_id=action,
                input_data=action_input,
                credentials=credentials,
            )

            return NodeExecutionResult(
                node_id=node_id,
                status="success",
                output={
                    "connector_slug": connector_slug,
                    "action": action,
                    "result": result,
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
                error=f"Connector execution failed: {str(e)}",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )


class ConditionActivityHandler(ActivityHandler):
    """Handler for condition/if-else nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
        execution_id: UUID | None = None,
        session: Session | None = None,
    ) -> NodeExecutionResult:
        """Execute condition node."""
        from datetime import datetime

        try:
            # Get condition expression from config
            condition_expr = node_config.get("condition") or node_config.get(
                "expression"
            )
            condition_type = node_config.get(
                "condition_type", "javascript"
            )  # javascript, python, jsonpath

            if not condition_expr:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="condition expression is required for condition node",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Evaluate condition
            result = self._evaluate_condition(
                condition_expr, condition_type, input_data
            )

            # Determine which branch to take
            branch = "true" if result else "false"

            return NodeExecutionResult(
                node_id=node_id,
                status="success",
                output={
                    "condition_result": result,
                    "branch": branch,
                    "condition_expr": condition_expr,
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
                error=f"Condition evaluation failed: {str(e)}",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )

    def _evaluate_condition(
        self, condition_expr: str, condition_type: str, input_data: dict[str, Any]
    ) -> bool:
        """Evaluate a condition expression."""
        if condition_type == "javascript":
            # Simple JavaScript-like evaluation
            # Replace variable references with values from input_data
            try:
                # Simple evaluation: replace ${var} with values
                eval_expr = condition_expr
                for key, value in input_data.items():
                    eval_expr = eval_expr.replace(f"${{{key}}}", str(value))
                    eval_expr = eval_expr.replace(f"${{data.{key}}}", str(value))

                # Evaluate as Python expression (limited safety)
                # In production, use a proper expression evaluator
                result = eval(eval_expr, {"__builtins__": {}}, {})
                return bool(result)
            except Exception:
                # Fallback: try direct evaluation
                return bool(eval(condition_expr, {"__builtins__": {}}, input_data))

        elif condition_type == "python":
            # Python expression evaluation
            try:
                result = eval(condition_expr, {"__builtins__": {}}, input_data)
                return bool(result)
            except Exception:
                return False

        elif condition_type == "jsonpath":
            # JSONPath evaluation (simplified)
            # For full JSONPath, use jsonpath-ng library
            try:
                # Simple path evaluation: data.path.to.value
                parts = condition_expr.split(".")
                value = input_data
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        return False
                return bool(value)
            except Exception:
                return False

        else:
            # Default: try Python evaluation
            try:
                result = eval(condition_expr, {"__builtins__": {}}, input_data)
                return bool(result)
            except Exception:
                return False


class AgentActivityHandler(ActivityHandler):
    """Handler for agent nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
        execution_id: UUID | None = None,
        session: Session | None = None,
    ) -> NodeExecutionResult:
        """Execute agent node."""
        from datetime import datetime

        if not session:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error="Database session required for agent execution",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )

        try:
            from app.agents.router import AgentRouter
            from app.models import Workflow, WorkflowExecution

            # Get user_id from execution -> workflow -> owner_id
            user_id = None
            if execution_id:
                execution = session.get(WorkflowExecution, execution_id)
                if execution:
                    workflow = session.get(Workflow, execution.workflow_id)
                    if workflow:
                        user_id = workflow.owner_id

            if not user_id:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="Could not determine user_id from execution context",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Get agent configuration
            agent_framework = node_config.get("framework") or node_config.get(
                "agent_framework"
            )
            task_type = node_config.get("task_type") or node_config.get("task")
            task_requirements = node_config.get("task_requirements", {})
            agent_id = node_config.get("agent_id")

            if not task_type:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="task_type is required for agent node",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Prepare task input data
            task_input = {**input_data}
            if "input_data" in node_config:
                task_input.update(node_config["input_data"])

            # Add user_id to task input
            task_input["user_id"] = str(user_id)

            # Execute agent task
            router = AgentRouter()
            task = router.execute_task(
                session=session,
                framework=agent_framework,
                task_type=task_type,
                input_data=task_input,
                agent_id=agent_id,
                user_id=user_id,
            )

            return NodeExecutionResult(
                node_id=node_id,
                status="success",
                output={
                    "task_id": str(task.id),
                    "framework": agent_framework or "auto",
                    "task_type": task_type,
                    "result": task.result,
                    "status": task.status,
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
                error=f"Agent execution failed: {str(e)}",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )


class SubWorkflowActivityHandler(ActivityHandler):
    """Handler for sub-workflow nodes."""

    def execute(
        self,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
        execution_id: UUID | None = None,
        session: Session | None = None,
    ) -> NodeExecutionResult:
        """Execute sub-workflow node."""
        from datetime import datetime
        from uuid import UUID as UUIDType

        if not session:
            return NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error="Database session required for sub-workflow execution",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )

        try:
            from app.models import Workflow
            from app.workflows.engine import WorkflowEngine

            # Get sub-workflow ID from config
            sub_workflow_id_str = node_config.get("workflow_id") or node_config.get(
                "sub_workflow_id"
            )

            if not sub_workflow_id_str:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error="workflow_id is required for sub-workflow node",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Parse workflow ID
            try:
                sub_workflow_id = UUIDType(sub_workflow_id_str)
            except ValueError:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error=f"Invalid workflow_id format: {sub_workflow_id_str}",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Verify sub-workflow exists
            sub_workflow = session.get(Workflow, sub_workflow_id)
            if not sub_workflow:
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error=f"Sub-workflow {sub_workflow_id} not found",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

            # Create execution for sub-workflow
            engine = WorkflowEngine()
            sub_execution = engine.create_execution(
                session=session,
                workflow_id=sub_workflow_id,
                trigger_data=input_data,
            )

            # Check if synchronous execution is requested
            wait_for_completion = node_config.get("wait_for_completion", False)

            if wait_for_completion:
                # Wait for sub-workflow to complete
                import time

                from app.models import WorkflowExecution as WorkflowExecutionModel

                max_wait_seconds = node_config.get(
                    "timeout_seconds", 3600
                )  # Default 1 hour
                poll_interval = 1.0  # Poll every second
                waited_seconds = 0

                while waited_seconds < max_wait_seconds:
                    # Check sub-workflow status
                    sub_exec = session.get(WorkflowExecutionModel, sub_execution.id)
                    if not sub_exec:
                        return NodeExecutionResult(
                            node_id=node_id,
                            status="failed",
                            output={},
                            error=f"Sub-workflow execution {sub_execution.id} not found",
                            started_at=datetime.utcnow(),
                            completed_at=datetime.utcnow(),
                            duration_ms=0,
                        )

                    if sub_exec.status in ("completed", "failed"):
                        # Sub-workflow completed
                        sub_state = engine.get_execution_state(
                            session, sub_execution.id
                        )
                        return NodeExecutionResult(
                            node_id=node_id,
                            status="success"
                            if sub_exec.status == "completed"
                            else "failed",
                            output={
                                "sub_workflow_id": str(sub_workflow_id),
                                "sub_execution_id": sub_execution.execution_id,
                                "sub_execution_uuid": str(sub_execution.id),
                                "status": sub_exec.status,
                                "result": sub_state.execution_data
                                if sub_exec.status == "completed"
                                else None,
                                "error": sub_exec.error_message
                                if sub_exec.status == "failed"
                                else None,
                            },
                            started_at=datetime.utcnow(),
                            completed_at=datetime.utcnow(),
                            duration_ms=int(waited_seconds * 1000),
                        )

                    # Wait before next poll
                    time.sleep(poll_interval)
                    waited_seconds += poll_interval
                    session.refresh(sub_exec)

                # Timeout
                return NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={
                        "sub_workflow_id": str(sub_workflow_id),
                        "sub_execution_id": sub_execution.execution_id,
                        "status": "timeout",
                    },
                    error=f"Sub-workflow execution timed out after {max_wait_seconds} seconds",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=int(waited_seconds * 1000),
                )
            else:
                # Asynchronous execution (original behavior)
                return NodeExecutionResult(
                    node_id=node_id,
                    status="success",
                    output={
                        "sub_workflow_id": str(sub_workflow_id),
                        "sub_execution_id": sub_execution.execution_id,
                        "sub_execution_uuid": str(sub_execution.id),
                        "status": "started",
                        "note": "Sub-workflow execution started asynchronously",
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
                error=f"Sub-workflow execution failed: {str(e)}",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
            )


# Activity handler registry
ACTIVITY_HANDLERS: dict[str, ActivityHandler] = {
    "trigger": TriggerActivityHandler(),
    "http_request": HTTPRequestActivityHandler(),
    "code": CodeActivityHandler(),
    "rag_switch": RAGSwitchActivityHandler(),
    "ocr_switch": OCRSwitchActivityHandler(),
    "connector": ConnectorActivityHandler(),
    "condition": ConditionActivityHandler(),
    "if": ConditionActivityHandler(),  # Alias for condition
    "switch": ConditionActivityHandler(),  # Alias for condition
    "agent": AgentActivityHandler(),
    "sub_workflow": SubWorkflowActivityHandler(),
    "sub-workflow": SubWorkflowActivityHandler(),  # Alias with hyphen
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
