"""
Supabase Storage Service

Handles file upload, download, and deletion using Supabase Storage.
"""
import logging
from datetime import datetime
from typing import Any, BinaryIO

from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageServiceError(Exception):
    """Base exception for storage service errors."""

    pass


class BucketNotFoundError(StorageServiceError):
    """Storage bucket not found."""

    pass


class FileNotFoundError(StorageServiceError):
    """File not found in storage."""

    pass


class StorageService:
    """
    Supabase Storage service for file management.

    Provides methods for:
    - Uploading files to Supabase Storage
    - Downloading files from Supabase Storage
    - Deleting files from Supabase Storage
    - Listing files in buckets
    - Generating signed URLs for file access
    """

    # Default buckets for different use cases
    BUCKETS = {
        "ocr_documents": "ocr-documents",
        "rag_files": "rag-files",
        "user_uploads": "user-uploads",
        "workflow_attachments": "workflow-attachments",
        "code_executions": "code-executions",
    }

    def __init__(self):
        """Initialize Supabase Storage client."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            logger.warning(
                "Supabase Storage not configured. SUPABASE_URL and SUPABASE_ANON_KEY required."
            )
            self.client: Client | None = None
            self.is_available = False
        else:
            try:
                self.client = create_client(
                    settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY
                )
                self.is_available = True
                logger.info("Supabase Storage client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase Storage client: {e}")
                self.client = None
                self.is_available = False

    def upload_file(
        self,
        bucket: str,
        file_path: str,
        file_data: bytes | BinaryIO,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Upload a file to Supabase Storage.

        Args:
            bucket: Bucket name (use BUCKETS constants or custom bucket)
            file_path: Path within the bucket (e.g., "user123/document.pdf")
            file_data: File data as bytes or file-like object
            content_type: Optional MIME type (e.g., "application/pdf")
            metadata: Optional file metadata

        Returns:
            Dictionary with file information:
            {
                "path": str,
                "url": str,
                "public_url": str | None,
                "size": int,
                "content_type": str,
            }

        Raises:
            StorageServiceError: If upload fails
        """
        if not self.is_available or not self.client:
            raise StorageServiceError(
                "Supabase Storage is not available. Check configuration."
            )

        try:
            # Ensure bucket exists (create if it doesn't)
            self._ensure_bucket_exists(bucket)

            # Convert file_data to bytes if it's a file-like object
            if hasattr(file_data, "read"):
                file_bytes = file_data.read()
            else:
                file_bytes = file_data

            # Upload file
            upload_response = self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_bytes,
                file_options={
                    "content-type": content_type or "application/octet-stream",
                    "upsert": True,  # Overwrite if exists
                    **({"metadata": metadata} if metadata else {}),
                },
            )

            # Get file info
            file_info = self.client.storage.from_(bucket).list(path=file_path)

            # Generate public URL if bucket is public
            public_url = None
            try:
                public_url_response = self.client.storage.from_(bucket).get_public_url(
                    file_path
                )
                public_url = public_url_response
            except Exception:
                # Bucket might be private, that's okay
                pass

            # Generate signed URL (works for both public and private buckets)
            signed_url = None
            try:
                signed_url_response = self.client.storage.from_(
                    bucket
                ).create_signed_url(
                    file_path,
                    expires_in=3600,  # 1 hour
                )
                signed_url = (
                    signed_url_response.get("signedURL")
                    if isinstance(signed_url_response, dict)
                    else signed_url_response
                )
            except Exception as e:
                logger.warning(f"Failed to generate signed URL: {e}")

            result = {
                "path": file_path,
                "url": signed_url
                or public_url
                or f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}",
                "public_url": public_url,
                "signed_url": signed_url,
                "size": len(file_bytes),
                "content_type": content_type or "application/octet-stream",
                "bucket": bucket,
                "uploaded_at": datetime.utcnow().isoformat(),
            }

            logger.info(
                f"File uploaded successfully: {bucket}/{file_path} ({len(file_bytes)} bytes)"
            )
            return result

        except Exception as e:
            logger.error(
                f"Failed to upload file to {bucket}/{file_path}: {e}", exc_info=True
            )
            raise StorageServiceError(f"File upload failed: {str(e)}")

    def download_file(
        self,
        bucket: str,
        file_path: str,
    ) -> bytes:
        """
        Download a file from Supabase Storage.

        Args:
            bucket: Bucket name
            file_path: Path within the bucket

        Returns:
            File data as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            StorageServiceError: If download fails
        """
        if not self.is_available or not self.client:
            raise StorageServiceError(
                "Supabase Storage is not available. Check configuration."
            )

        try:
            file_data = self.client.storage.from_(bucket).download(file_path)

            if isinstance(file_data, bytes):
                return file_data
            elif isinstance(file_data, str):
                return file_data.encode("utf-8")
            else:
                # If it's a response object, read it
                return (
                    file_data.read() if hasattr(file_data, "read") else bytes(file_data)
                )

        except Exception as e:
            logger.error(
                f"Failed to download file from {bucket}/{file_path}: {e}", exc_info=True
            )
            if "not found" in str(e).lower() or "404" in str(e):
                raise FileNotFoundError(f"File not found: {bucket}/{file_path}")
            raise StorageServiceError(f"File download failed: {str(e)}")

    def delete_file(
        self,
        bucket: str,
        file_path: str,
    ) -> None:
        """
        Delete a file from Supabase Storage.

        Args:
            bucket: Bucket name
            file_path: Path within the bucket

        Raises:
            FileNotFoundError: If file doesn't exist
            StorageServiceError: If deletion fails
        """
        if not self.is_available or not self.client:
            raise StorageServiceError(
                "Supabase Storage is not available. Check configuration."
            )

        try:
            self.client.storage.from_(bucket).remove([file_path])
            logger.info(f"File deleted successfully: {bucket}/{file_path}")

        except Exception as e:
            logger.error(
                f"Failed to delete file from {bucket}/{file_path}: {e}", exc_info=True
            )
            if "not found" in str(e).lower() or "404" in str(e):
                raise FileNotFoundError(f"File not found: {bucket}/{file_path}")
            raise StorageServiceError(f"File deletion failed: {str(e)}")

    def list_files(
        self,
        bucket: str,
        folder_path: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        List files in a bucket folder.

        Args:
            bucket: Bucket name
            folder_path: Folder path within bucket (empty for root)
            limit: Maximum number of files to return
            offset: Offset for pagination

        Returns:
            List of file information dictionaries
        """
        if not self.is_available or not self.client:
            raise StorageServiceError(
                "Supabase Storage is not available. Check configuration."
            )

        try:
            files = self.client.storage.from_(bucket).list(
                path=folder_path,
                limit=limit,
                offset=offset,
            )

            result = []
            for file_info in files:
                if isinstance(file_info, dict):
                    result.append(
                        {
                            "name": file_info.get("name"),
                            "path": f"{folder_path}/{file_info.get('name')}"
                            if folder_path
                            else file_info.get("name"),
                            "size": file_info.get("metadata", {}).get("size"),
                            "content_type": file_info.get("metadata", {}).get(
                                "mimetype"
                            ),
                            "created_at": file_info.get("created_at"),
                            "updated_at": file_info.get("updated_at"),
                        }
                    )

            return result

        except Exception as e:
            logger.error(
                f"Failed to list files in {bucket}/{folder_path}: {e}", exc_info=True
            )
            raise StorageServiceError(f"Failed to list files: {str(e)}")

    def get_public_url(
        self,
        bucket: str,
        file_path: str,
    ) -> str:
        """
        Get public URL for a file (works only for public buckets).

        Args:
            bucket: Bucket name
            file_path: Path within the bucket

        Returns:
            Public URL string
        """
        if not self.is_available or not self.client:
            raise StorageServiceError(
                "Supabase Storage is not available. Check configuration."
            )

        try:
            return self.client.storage.from_(bucket).get_public_url(file_path)
        except Exception as e:
            logger.error(
                f"Failed to get public URL for {bucket}/{file_path}: {e}", exc_info=True
            )
            raise StorageServiceError(f"Failed to get public URL: {str(e)}")

    def create_signed_url(
        self,
        bucket: str,
        file_path: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Create a signed URL for temporary file access (works for both public and private buckets).

        Args:
            bucket: Bucket name
            file_path: Path within the bucket
            expires_in: Expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL string
        """
        if not self.is_available or not self.client:
            raise StorageServiceError(
                "Supabase Storage is not available. Check configuration."
            )

        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                file_path,
                expires_in=expires_in,
            )

            if isinstance(response, dict):
                return response.get("signedURL", "")
            return str(response)

        except Exception as e:
            logger.error(
                f"Failed to create signed URL for {bucket}/{file_path}: {e}",
                exc_info=True,
            )
            raise StorageServiceError(f"Failed to create signed URL: {str(e)}")

    def _ensure_bucket_exists(self, bucket: str) -> None:
        """
        Ensure a bucket exists, create it if it doesn't.

        Args:
            bucket: Bucket name
        """
        if not self.is_available or not self.client:
            return

        try:
            # Try to list files in bucket (this will fail if bucket doesn't exist)
            self.client.storage.from_(bucket).list(limit=1)
        except Exception:
            # Bucket doesn't exist, try to create it
            try:
                # Note: Bucket creation typically requires admin privileges
                # In Supabase, buckets are usually created via dashboard or admin API
                logger.warning(
                    f"Bucket '{bucket}' may not exist. Create it in Supabase Dashboard: Storage > New Bucket"
                )
            except Exception as e:
                logger.warning(
                    f"Could not verify/create bucket '{bucket}': {e}. Ensure bucket exists in Supabase Dashboard."
                )


# Default storage service instance
default_storage_service = StorageService()
