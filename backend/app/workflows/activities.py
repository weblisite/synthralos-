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
        # TODO: Implement HTTP request logic
        # For now, return placeholder
        from datetime import datetime
        
        return NodeExecutionResult(
            node_id=node_id,
            status="success",
            output={"message": "HTTP request placeholder"},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=0,
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
        # TODO: Implement code execution logic
        # For now, return placeholder
        from datetime import datetime
        
        return NodeExecutionResult(
            node_id=node_id,
            status="success",
            output={"message": "Code execution placeholder"},
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
        
        # Note: This handler doesn't have direct access to database session
        # The workflow engine should pass session if needed, or we use a service
        # For now, we'll use the RAG service which will handle session internally
        from app.rag.service import default_rag_service
        from app.core.db import engine
        from sqlmodel import Session
        
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
            index_id = UUID(index_id_str) if isinstance(index_id_str, str) else index_id_str
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
        
        layout_type = query_requirements.get("layout") or document_metadata.get("layout")
        handwriting_detected = query_requirements.get("handwriting_detected", False)
        heavy_pdf_or_image = query_requirements.get("heavy_pdf_or_image", False)
        region = query_requirements.get("region") or document_metadata.get("region")
        latency_requirement = query_requirements.get("latency_ms", 0)
        structured_json_required = query_requirements.get("structured_json_required", False)
        
        # Check requirements
        if structured_json_required:
            reasons.append("Structured JSON required → Omniparser")
        
        if layout_type == "table":
            reasons.append(f"Table layout detected → DocTR")
        
        if handwriting_detected:
            reasons.append("Handwriting detected → EasyOCR")
        
        if heavy_pdf_or_image:
            reasons.append("Heavy PDF/image → Google Vision API")
        
        if region == "EU" or latency_requirement > 1000:
            reasons.append(f"EU region or latency > 1s → PaddleOCR")
        
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

