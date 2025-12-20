"""
OCR API Routes

Endpoints for OCR (Optical Character Recognition) operations:
- Extract text from documents
- Get job status
- Batch processing
"""

import uuid
from typing import Any

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, SessionDep
from app.ocr.service import (
    JobNotFoundError,
    OCRServiceError,
    default_ocr_service,
)

router = APIRouter(prefix="/ocr", tags=["ocr"])


# ============================================================================
# Request/Response Models
# ============================================================================


class OCRExtractRequest(BaseModel):
    """Request model for OCR extraction."""

    document_url: str = Field(max_length=1000)
    engine: str | None = Field(default=None, max_length=100)
    document_metadata: dict[str, Any] = Field(default_factory=dict)
    query_requirements: dict[str, Any] = Field(default_factory=dict)


class OCRJobResponse(BaseModel):
    """Response model for OCR job."""

    id: str
    document_url: str
    engine: str
    status: str
    started_at: str
    completed_at: str | None = None
    error_message: str | None = None


class OCRResultResponse(BaseModel):
    """Response model for OCR result."""

    id: str
    job_id: str
    extracted_text: str
    structured_data: dict[str, Any] | None = None
    confidence_score: float | None = None
    created_at: str


class OCRBatchRequest(BaseModel):
    """Request model for batch OCR processing."""

    document_urls: list[str] = Field(min_items=1, max_items=100)
    engine: str | None = Field(default=None, max_length=100)
    document_metadata: dict[str, Any] = Field(default_factory=dict)
    query_requirements: dict[str, Any] = Field(default_factory=dict)


class OCRBatchResponse(BaseModel):
    """Response model for batch OCR processing."""

    jobs: list[OCRJobResponse]
    total_count: int


class OCRUploadRequest(BaseModel):
    """Request model for OCR file upload."""

    engine: str | None = Field(default=None, max_length=100)
    document_metadata: dict[str, Any] = Field(default_factory=dict)
    query_requirements: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/upload", response_model=OCRJobResponse, status_code=status.HTTP_201_CREATED
)
async def upload_and_extract(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    engine: str | None = None,
    document_metadata: dict[str, Any] | None = None,
    query_requirements: dict[str, Any] | None = None,
) -> Any:
    """
    Upload a file and extract text using OCR.

    Uploads file to Supabase Storage, then creates an OCR job.
    The job will be processed asynchronously.
    """
    from app.services.storage import default_storage_service

    if not default_storage_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Check Supabase configuration.",
        )

    try:
        # Read file data
        file_data = await file.read()

        # Generate storage path: ocr-documents/{user_id}/{filename}
        storage_path = f"{current_user.id}/{file.filename}"
        bucket = "ocr-documents"

        # Upload to Supabase Storage
        upload_result = default_storage_service.upload_file(
            bucket=bucket,
            file_path=storage_path,
            file_data=file_data,
            content_type=file.content_type or "application/octet-stream",
            metadata={
                "user_id": str(current_user.id),
                "original_filename": file.filename,
                "uploaded_by": current_user.email,
            },
        )

        # Create OCR job from storage
        if not document_metadata:
            document_metadata = {}
        document_metadata["storage_bucket"] = bucket
        document_metadata["storage_path"] = storage_path

        job = default_ocr_service.create_job_from_storage(
            session=session,
            storage_path=storage_path,
            bucket=bucket,
            engine=engine,
            document_metadata=document_metadata,
            query_requirements=query_requirements or {},
        )

        return {
            "id": str(job.id),
            "document_url": upload_result.get("url") or job.document_url,
            "engine": job.engine,
            "status": job.status,
            "started_at": job.started_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
        }
    except OCRServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload and OCR job creation failed: {str(e)}",
        )


@router.post(
    "/extract", response_model=OCRJobResponse, status_code=status.HTTP_201_CREATED
)
def extract_text(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    extract_in: OCRExtractRequest,
) -> Any:
    """
    Extract text from a document using OCR (from URL).

    Creates an OCR job and returns the job ID.
    The job will be processed asynchronously.
    """
    try:
        job = default_ocr_service.create_job(
            session=session,
            document_url=extract_in.document_url,
            engine=extract_in.engine,
            document_metadata=extract_in.document_metadata,
            query_requirements=extract_in.query_requirements,
        )

        return {
            "id": str(job.id),
            "document_url": job.document_url,
            "engine": job.engine,
            "status": job.status,
            "started_at": job.started_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
        }
    except OCRServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/status/{job_id}", response_model=OCRJobResponse)
def get_job_status(
    job_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get OCR job status by ID.
    """
    try:
        job = default_ocr_service.get_job(session=session, job_id=job_id)

        return {
            "id": str(job.id),
            "document_url": job.document_url,
            "engine": job.engine,
            "status": job.status,
            "started_at": job.started_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
        }
    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR job not found",
        )
    except OCRServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/result/{job_id}", response_model=OCRResultResponse)
def get_job_result(
    job_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get OCR result for a job.

    Returns the extracted text and structured data if the job is completed.
    """
    try:
        job = default_ocr_service.get_job(session=session, job_id=job_id)

        if job.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OCR job is not completed. Current status: {job.status}",
            )

        result = default_ocr_service.get_job_result(session=session, job_id=job_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OCR result not found",
            )

        return {
            "id": str(result.id),
            "job_id": str(result.job_id),
            "extracted_text": result.extracted_text,
            "structured_data": result.structured_data,
            "confidence_score": result.confidence_score,
            "created_at": result.created_at.isoformat(),
        }
    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR job not found",
        )
    except OCRServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/batch", response_model=OCRBatchResponse, status_code=status.HTTP_201_CREATED
)
def batch_extract(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    batch_in: OCRBatchRequest,
) -> Any:
    """
    Create multiple OCR jobs for batch processing.

    Creates OCR jobs for multiple documents and returns all job IDs.
    """
    try:
        jobs = default_ocr_service.batch_process(
            session=session,
            document_urls=batch_in.document_urls,
            engine=batch_in.engine,
            document_metadata=batch_in.document_metadata,
            query_requirements=batch_in.query_requirements,
        )

        return {
            "jobs": [
                {
                    "id": str(job.id),
                    "document_url": job.document_url,
                    "engine": job.engine,
                    "status": job.status,
                    "started_at": job.started_at.isoformat(),
                    "completed_at": job.completed_at.isoformat()
                    if job.completed_at
                    else None,
                    "error_message": job.error_message,
                }
                for job in jobs
            ],
            "total_count": len(jobs),
        }
    except OCRServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/process/{job_id}", response_model=OCRResultResponse)
def process_job(
    job_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Process an OCR job synchronously.

    This endpoint will process the OCR job immediately and return the result.
    Use this for small documents or when you need immediate results.
    """
    try:
        result = default_ocr_service.process_job(session=session, job_id=job_id)

        return {
            "id": str(result.id),
            "job_id": str(result.job_id),
            "extracted_text": result.extracted_text,
            "structured_data": result.structured_data,
            "confidence_score": result.confidence_score,
            "created_at": result.created_at.isoformat(),
        }
    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR job not found",
        )
    except OCRServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/jobs", response_model=list[OCRJobResponse])
def list_jobs(
    session: SessionDep,
    current_user: CurrentUser,
    status: str | None = Query(default=None, description="Filter by job status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> Any:
    """
    List OCR jobs.

    Returns a list of OCR jobs with optional status filtering.
    """
    try:
        jobs = default_ocr_service.list_jobs(
            session=session,
            status=status,
            skip=skip,
            limit=limit,
        )

        return [
            {
                "id": str(job.id),
                "document_url": job.document_url,
                "engine": job.engine,
                "status": job.status,
                "started_at": job.started_at.isoformat(),
                "completed_at": job.completed_at.isoformat()
                if job.completed_at
                else None,
                "error_message": job.error_message,
            }
            for job in jobs
        ]
    except OCRServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
