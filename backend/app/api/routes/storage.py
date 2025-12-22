"""
Storage API Routes

Endpoints for Supabase Storage operations:
- Upload files
- Download files
- Delete files
- List files
- Get signed URLs
"""
import uuid
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, SessionDep
from app.services.storage import (
    FileNotFoundError,
    StorageServiceError,
    default_storage_service,
)

router = APIRouter(prefix="/storage", tags=["storage"])


# ============================================================================
# Request/Response Models
# ============================================================================


class FileUploadRequest(BaseModel):
    """Request model for file upload."""

    bucket: str = Field(max_length=100)
    folder_path: str = Field(default="", max_length=1000)
    content_type: str | None = Field(default=None, max_length=100)


class FileUploadResponse(BaseModel):
    """Response model for file upload."""

    file_id: str
    path: str
    url: str
    public_url: str | None = None
    signed_url: str | None = None
    size: int
    content_type: str
    bucket: str
    uploaded_at: str


class FileDownloadResponse(BaseModel):
    """Response model for file download."""

    file_data: str  # Base64 encoded
    content_type: str
    filename: str


class FileListResponse(BaseModel):
    """Response model for file listing."""

    files: list[dict[str, Any]]
    total_count: int
    bucket: str
    folder_path: str


class SignedUrlRequest(BaseModel):
    """Request model for signed URL generation."""

    bucket: str = Field(max_length=100)
    file_path: str = Field(max_length=1000)
    expires_in: int = Field(default=3600, ge=60, le=604800)  # 1 minute to 7 days


class SignedUrlResponse(BaseModel):
    """Response model for signed URL."""

    signed_url: str
    expires_in: int


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    bucket: str,
    file: UploadFile = File(...),
    folder_path: str = "",
    content_type: str | None = None,
) -> Any:
    """
    Upload a file to Supabase Storage.

    Files are organized by bucket and optional folder path.
    Default buckets:
    - ocr-documents: For OCR job documents
    - rag-files: For RAG document files
    - user-uploads: For user-uploaded files
    - workflow-attachments: For workflow attachments
    - code-executions: For code execution files
    """
    if not default_storage_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Check Supabase configuration.",
        )

    try:
        # Read file data
        file_data = await file.read()

        # Generate file path: {folder_path}/{user_id}/{filename}
        # If folder_path is empty, use user_id as folder
        if folder_path:
            file_path = f"{folder_path}/{current_user.id}/{file.filename}"
        else:
            file_path = f"{current_user.id}/{file.filename}"

        # Use provided content_type or detect from filename
        if not content_type:
            content_type = file.content_type or "application/octet-stream"

        # Upload to Supabase Storage
        upload_result = default_storage_service.upload_file(
            bucket=bucket,
            file_path=file_path,
            file_data=file_data,
            content_type=content_type,
            metadata={
                "user_id": str(current_user.id),
                "original_filename": file.filename,
                "uploaded_by": current_user.email,
            },
        )

        return {
            "file_id": str(uuid.uuid4()),  # Generate a file ID for reference
            **upload_result,
        }

    except StorageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )


@router.get("/download/{bucket}/{file_path:path}")
async def download_file(
    bucket: str,
    file_path: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Download a file from Supabase Storage.

    Returns file as binary data with appropriate content type.
    """
    if not default_storage_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Check Supabase configuration.",
        )

    try:
        file_data = default_storage_service.download_file(
            bucket=bucket, file_path=file_path
        )

        # Determine content type from file extension
        import mimetypes

        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"

        from fastapi.responses import Response

        return Response(
            content=file_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_path.split("/")[-1]}"',
            },
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    except StorageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/delete/{bucket}/{file_path:path}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_file(
    bucket: str,
    file_path: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    """
    Delete a file from Supabase Storage.

    Returns 204 No Content on successful deletion.
    """
    if not default_storage_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Check Supabase configuration.",
        )

    try:
        default_storage_service.delete_file(bucket=bucket, file_path=file_path)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    except StorageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/list/{bucket}", response_model=FileListResponse)
async def list_files(
    bucket: str,
    session: SessionDep,
    current_user: CurrentUser,
    folder_path: str = "",
    limit: int = 100,
    offset: int = 0,
) -> Any:
    """
    List files in a Supabase Storage bucket.
    """
    if not default_storage_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Check Supabase configuration.",
        )

    try:
        files = default_storage_service.list_files(
            bucket=bucket,
            folder_path=folder_path,
            limit=limit,
            offset=offset,
        )

        return {
            "files": files,
            "total_count": len(files),
            "bucket": bucket,
            "folder_path": folder_path,
        }

    except StorageServiceError as e:
        logger.error(f"Storage service error listing files in bucket {bucket}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error listing files in bucket {bucket}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}",
        )


@router.post("/signed-url", response_model=SignedUrlResponse)
async def create_signed_url(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    request: SignedUrlRequest,
) -> Any:
    """
    Create a signed URL for temporary file access.

    Useful for accessing private files or generating temporary download links.
    """
    if not default_storage_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Check Supabase configuration.",
        )

    try:
        signed_url = default_storage_service.create_signed_url(
            bucket=request.bucket,
            file_path=request.file_path,
            expires_in=request.expires_in,
        )

        return {
            "signed_url": signed_url,
            "expires_in": request.expires_in,
        }

    except StorageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/buckets")
async def list_buckets(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    List available storage buckets.
    """
    return {
        "buckets": list(default_storage_service.BUCKETS.values()),
        "bucket_info": {
            bucket_name: {
                "description": f"Storage bucket for {category.replace('_', ' ')}",
                "category": category,
            }
            for category, bucket_name in default_storage_service.BUCKETS.items()
        },
    }
