"""
RAG API Routes

Endpoints for RAG (Retrieval-Augmented Generation) operations:
- Query RAG indexes
- Create/manage indexes
- Evaluate routing decisions
- View routing logs
"""

import uuid
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, UploadFile, File, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep
from app.models import RAGIndex, RAGQuery, RAGSwitchLog
from app.rag.service import (
    IndexNotFoundError,
    RAGServiceError,
    default_rag_service,
)


router = APIRouter(prefix="/rag", tags=["rag"])


# ============================================================================
# Request/Response Models
# ============================================================================


class RAGIndexCreate(BaseModel):
    """Request model for creating a RAG index."""
    name: str = Field(max_length=255)
    vector_db_type: str = Field(max_length=50, default="chromadb")


class RAGIndexPublic(BaseModel):
    """Public RAG index model."""
    id: uuid.UUID
    name: str
    vector_db_type: str
    owner_id: uuid.UUID
    created_at: str

    class Config:
        from_attributes = True


class RAGQueryRequest(BaseModel):
    """Request model for RAG query."""
    index_id: uuid.UUID
    query_text: str = Field(max_length=5000)
    top_k: int = Field(default=5, ge=1, le=100)
    query_requirements: dict[str, Any] = Field(default_factory=dict)


class RAGQueryResponse(BaseModel):
    """Response model for RAG query."""
    query_id: str
    vector_db: str
    results: dict[str, Any]
    latency_ms: int


class RAGSwitchEvaluateRequest(BaseModel):
    """Request model for evaluating RAG routing."""
    index_id: uuid.UUID
    query_requirements: dict[str, Any] = Field(default_factory=dict)


class RAGSwitchEvaluateResponse(BaseModel):
    """Response model for RAG routing evaluation."""
    selected_vector_db: str
    routing_reason: str
    index_statistics: dict[str, Any]
    query_requirements: dict[str, Any]


class RAGDocumentAddRequest(BaseModel):
    """Request model for adding a document to a RAG index."""
    index_id: uuid.UUID
    content: str = Field(max_length=100000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] | None = None


class RAGDocumentAddResponse(BaseModel):
    """Response model for adding a document."""
    document_id: str
    index_id: str


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/index", response_model=RAGIndexPublic, status_code=status.HTTP_201_CREATED)
def create_index(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    index_in: RAGIndexCreate,
) -> Any:
    """
    Create a new RAG index.
    """
    index = default_rag_service.create_index(
        session=session,
        name=index_in.name,
        vector_db_type=index_in.vector_db_type,
        owner_id=current_user.id,
    )
    return index


@router.get("/indexes", response_model=list[RAGIndexPublic])
def list_indexes(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> Any:
    """
    List RAG indexes for the current user.
    """
    indexes = default_rag_service.list_indexes(
        session=session,
        owner_id=current_user.id,
    )
    return indexes[skip : skip + limit]


@router.get("/index/{index_id}", response_model=RAGIndexPublic)
def get_index(
    index_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get a RAG index by ID.
    """
    index = default_rag_service.get_index(session=session, index_id=index_id)
    
    # Check ownership
    if index.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return index


@router.post("/query", response_model=RAGQueryResponse)
def query_index(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    query_in: RAGQueryRequest,
) -> Any:
    """
    Query a RAG index.
    
    Automatically routes to the appropriate vector database based on:
    - Dataset size
    - Query requirements
    - User plan
    """
    # Verify index exists and user has access
    index = default_rag_service.get_index(session=session, index_id=query_in.index_id)
    
    if index.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        result = default_rag_service.query(
            session=session,
            index_id=query_in.index_id,
            query_text=query_in.query_text,
            top_k=query_in.top_k,
            query_requirements=query_in.query_requirements,
        )
        return result
    except IndexNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG index not found",
        )
    except RAGServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/switch/evaluate", response_model=RAGSwitchEvaluateResponse)
def evaluate_routing(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    evaluate_in: RAGSwitchEvaluateRequest,
) -> Any:
    """
    Evaluate routing decision for a RAG query without executing it.
    
    Useful for understanding which vector database would be selected
    for a given query and index.
    """
    # Verify index exists and user has access
    index = default_rag_service.get_index(session=session, index_id=evaluate_in.index_id)
    
    if index.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        evaluation = default_rag_service.evaluate_routing(
            session=session,
            index_id=evaluate_in.index_id,
            query_requirements=evaluate_in.query_requirements,
        )
        return evaluation
    except IndexNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG index not found",
        )
    except RAGServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/document/upload", response_model=RAGDocumentAddResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    index_id: uuid.UUID,
    file: UploadFile = File(...),
    metadata: dict[str, Any] | None = None,
    embedding: list[float] | None = None,
) -> Any:
    """
    Upload a file and add it to a RAG index.
    
    Uploads file to Supabase Storage, then adds it to the RAG index.
    """
    from app.services.storage import default_storage_service
    
    if not default_storage_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Check Supabase configuration.",
        )
    
    # Verify index exists and user has access
    index = default_rag_service.get_index(session=session, index_id=index_id)
    
    if index.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        # Read file data
        file_data = await file.read()
        
        # Generate storage path: rag-files/{user_id}/{index_id}/{filename}
        storage_path = f"{current_user.id}/{index_id}/{file.filename}"
        bucket = "rag-files"
        
        # Upload to Supabase Storage
        upload_result = default_storage_service.upload_file(
            bucket=bucket,
            file_path=storage_path,
            file_data=file_data,
            content_type=file.content_type or "text/plain",
            metadata={
                "user_id": str(current_user.id),
                "index_id": str(index_id),
                "original_filename": file.filename,
                "uploaded_by": current_user.email,
            },
        )
        
        # Add storage info to metadata
        if not metadata:
            metadata = {}
        metadata["storage_bucket"] = bucket
        metadata["storage_path"] = storage_path
        
        # Add document from storage
        document = default_rag_service.add_document_from_storage(
            session=session,
            index_id=index_id,
            storage_path=storage_path,
            bucket=bucket,
            metadata=metadata,
            embedding=embedding,
        )
        
        return {
            "document_id": str(document.id),
            "index_id": str(document.index_id),
        }
    except IndexNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG index not found",
        )
    except RAGServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload and document addition failed: {str(e)}",
        )


@router.post("/document", response_model=RAGDocumentAddResponse, status_code=status.HTTP_201_CREATED)
def add_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    document_in: RAGDocumentAddRequest,
) -> Any:
    """
    Add a document to a RAG index (from text content).
    """
    # Verify index exists and user has access
    index = default_rag_service.get_index(session=session, index_id=document_in.index_id)
    
    if index.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        document = default_rag_service.add_document(
            session=session,
            index_id=document_in.index_id,
            content=document_in.content,
            metadata=document_in.metadata,
            embedding=document_in.embedding,
        )
        return {
            "document_id": str(document.id),
            "index_id": str(document.index_id),
        }
    except IndexNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG index not found",
        )
    except RAGServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/switch/logs")
def get_routing_logs(
    session: SessionDep,
    current_user: CurrentUser,
    index_id: uuid.UUID | None = Query(default=None),
    query_id: uuid.UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> Any:
    """
    Get routing decision logs.
    
    Returns logs of routing decisions made for RAG queries.
    """
    statement = select(RAGSwitchLog)
    
    # Filter by index_id if provided (via query_id -> query -> index_id)
    if index_id:
        # Get queries for this index
        queries = session.exec(
            select(RAGQuery).where(RAGQuery.index_id == index_id)
        ).all()
        query_ids = [q.id for q in queries]
        
        # Verify user owns the index
        index = session.get(RAGIndex, index_id)
        if not index:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RAG index not found",
            )
        if index.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        
        if query_ids:
            statement = statement.where(RAGSwitchLog.query_id.in_(query_ids))
        else:
            # No queries for this index, return empty
            return []
    
    # Filter by query_id if provided
    if query_id:
        # Verify user owns the query's index
        query = session.get(RAGQuery, query_id)
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RAG query not found",
            )
        index = session.get(RAGIndex, query.index_id)
        if index and index.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        statement = statement.where(RAGSwitchLog.query_id == query_id)
    
    # If no filters, only show logs for user's indexes
    if not index_id and not query_id:
        # Get all user's indexes
        user_indexes = default_rag_service.list_indexes(
            session=session,
            owner_id=current_user.id,
        )
        user_index_ids = [idx.id for idx in user_indexes]
        
        if user_index_ids:
            # Get queries for user's indexes
            queries = session.exec(
                select(RAGQuery).where(RAGQuery.index_id.in_(user_index_ids))
            ).all()
            query_ids = [q.id for q in queries]
            
            if query_ids:
                statement = statement.where(RAGSwitchLog.query_id.in_(query_ids))
            else:
                return []
        else:
            return []
    
    # Order by created_at descending
    statement = statement.order_by(RAGSwitchLog.created_at.desc())
    
    # Apply pagination
    logs = session.exec(statement.offset(skip).limit(limit)).all()
    
    return [
        {
            "id": str(log.id),
            "query_id": str(log.query_id) if log.query_id else None,
            "routing_decision": log.routing_decision,
            "routing_reason": log.routing_reason,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.get("/query/{query_id}")
def get_query(
    query_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get a RAG query by ID.
    """
    query = session.get(RAGQuery, query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG query not found",
        )
    
    # Verify user owns the query's index
    index = session.get(RAGIndex, query.index_id)
    if index and index.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return {
        "id": str(query.id),
        "index_id": str(query.index_id),
        "query_text": query.query_text,
        "results": query.results,
        "latency_ms": query.latency_ms,
        "created_at": query.created_at.isoformat(),
    }


@router.post("/agent0/validate", status_code=status.HTTP_200_OK)
def validate_agent0_prompt(
    session: SessionDep,
    current_user: CurrentUser,
    prompt: str = Body(...),
    context: dict[str, Any] | None = Body(None),
) -> Any:
    """
    Validate an Agent0 prompt for RAG usage.
    
    Agent0 is a belief/goal reactive agent framework that can use RAG
    for context retrieval. This endpoint validates that a prompt is
    suitable for Agent0 execution with RAG.
    
    Request Body:
    - prompt: Agent0 prompt to validate
    - context: Optional context dictionary
    
    Returns:
    - Validation result with suggestions
    """
    # Basic validation logic
    validation_result = {
        "is_valid": True,
        "warnings": [],
        "suggestions": [],
    }
    
    # Check prompt length
    if len(prompt) < 10:
        validation_result["is_valid"] = False
        validation_result["warnings"].append("Prompt is too short (minimum 10 characters)")
    
    if len(prompt) > 10000:
        validation_result["warnings"].append("Prompt is very long (over 10k characters)")
        validation_result["suggestions"].append("Consider breaking into smaller prompts")
    
    # Check for RAG-related keywords
    rag_keywords = ["retrieve", "search", "find", "query", "context", "knowledge", "information"]
    has_rag_intent = any(keyword in prompt.lower() for keyword in rag_keywords)
    
    if not has_rag_intent:
        validation_result["suggestions"].append(
            "Prompt doesn't seem to require RAG. Consider if RAG is necessary."
        )
    
    # Check for Agent0-specific patterns
    agent0_patterns = ["goal", "belief", "plan", "action", "state"]
    has_agent0_patterns = any(pattern in prompt.lower() for pattern in agent0_patterns)
    
    if not has_agent0_patterns:
        validation_result["suggestions"].append(
            "Prompt may not be optimized for Agent0. Consider adding goal/belief context."
        )
    
    return {
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,  # Truncate for response
        "validation": validation_result,
        "recommended_index_type": "chromadb" if len(prompt) < 1000 else "milvus",
    }


@router.post("/finetune", status_code=status.HTTP_201_CREATED)
def start_finetune_job(
    session: SessionDep,
    current_user: CurrentUser,
    index_id: uuid.UUID = Body(...),
    config: dict[str, Any] = Body(default_factory=dict),
    dataset_urls: list[str] = Body(default_factory=list),
) -> Any:
    """
    Start a RAG fine-tuning job.
    
    Request Body:
    - index_id: RAG index ID to fine-tune
    - config: Fine-tuning configuration
    - dataset_urls: List of dataset URLs for training
    
    Returns:
    - Fine-tuning job details
    """
    from app.models import RAGFinetuneJob, RAGFinetuneDataset
    
    # Verify user owns the index
    index = session.get(RAGIndex, index_id)
    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG index not found",
        )
    
    if index.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Create fine-tuning job
    job = RAGFinetuneJob(
        index_id=index_id,
        status="running",
        config=config,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    
    # Create dataset records
    datasets = []
    for dataset_url in dataset_urls:
        dataset = RAGFinetuneDataset(
            job_id=job.id,
            dataset_url=dataset_url,
        )
        session.add(dataset)
        datasets.append(dataset)
    
    session.commit()
    
    # TODO: Start actual fine-tuning process (background task)
    # For now, this is a placeholder that creates the job record
    
    return {
        "id": str(job.id),
        "index_id": str(index_id),
        "status": job.status,
        "config": job.config,
        "dataset_count": len(datasets),
        "started_at": job.started_at.isoformat(),
    }

