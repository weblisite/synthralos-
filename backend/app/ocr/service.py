"""
OCR Service

Multi-engine OCR routing and document extraction service.
Handles routing logic for multiple OCR engines.
"""

import io
import logging
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from sqlmodel import Session, select

from app.core.config import settings
from app.models import OCRDocument, OCRJob, OCRResult

logger = logging.getLogger(__name__)


class OCRServiceError(Exception):
    """Base exception for OCR service errors."""
    pass


class JobNotFoundError(OCRServiceError):
    """OCR job not found."""
    pass


class EngineNotAvailableError(OCRServiceError):
    """OCR engine not available."""
    pass


class OCRService:
    """
    OCR service for multi-engine document extraction.
    
    Routing Logic:
    - layout = table → DocTR
    - handwriting_detected = true → EasyOCR
    - heavy_pdf_or_image = true → Google Vision
    - region = EU / latency > 1s → PaddleOCR
    - result = empty → Tesseract (fallback)
    - structured_json_required = true → Omniparser
    """
    
    def __init__(self):
        """Initialize OCR service."""
        self._ocr_engines: dict[str, Any] = {}
        self._initialize_engines()
    
    def _initialize_engines(self) -> None:
        """Initialize available OCR engines."""
        # Tesseract
        try:
            import pytesseract
            # Check if Tesseract is available
            try:
                pytesseract.get_tesseract_version()
                self._ocr_engines["tesseract"] = {
                    "name": "tesseract",
                    "is_available": True,
                    "client": pytesseract,
                }
                logger.info("✅ Tesseract OCR engine initialized")
            except Exception as e:
                logger.warning(f"Tesseract not available: {e}")
                self._ocr_engines["tesseract"] = {
                    "name": "tesseract",
                    "is_available": False,
                }
        except ImportError:
            logger.info("pytesseract not installed. Install with: pip install pytesseract")
            self._ocr_engines["tesseract"] = {
                "name": "tesseract",
                "is_available": False,
            }
        
        # EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)  # Initialize with English, no GPU
            self._ocr_engines["easyocr"] = {
                "name": "easyocr",
                "is_available": True,
                "client": reader,
            }
            logger.info("✅ EasyOCR engine initialized")
        except ImportError:
            logger.info("easyocr not installed. Install with: pip install easyocr")
            self._ocr_engines["easyocr"] = {
                "name": "easyocr",
                "is_available": False,
            }
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            self._ocr_engines["easyocr"] = {
                "name": "easyocr",
                "is_available": False,
            }
        
        # Google Vision API
        if settings.GOOGLE_VISION_API_KEY:
            try:
                from google.cloud import vision
                client = vision.ImageAnnotatorClient()
                self._ocr_engines["google_vision"] = {
                    "name": "google_vision",
                    "is_available": True,
                    "client": client,
                }
                logger.info("✅ Google Vision API OCR engine initialized")
            except ImportError:
                logger.info("google-cloud-vision not installed. Install with: pip install google-cloud-vision")
                self._ocr_engines["google_vision"] = {
                    "name": "google_vision",
                    "is_available": False,
                }
            except Exception as e:
                logger.warning(f"Google Vision API initialization failed: {e}")
                self._ocr_engines["google_vision"] = {
                    "name": "google_vision",
                    "is_available": False,
                }
        else:
            self._ocr_engines["google_vision"] = {
                "name": "google_vision",
                "is_available": False,
            }
    
    def select_engine(
        self,
        document_url: str,
        document_metadata: dict[str, Any] | None = None,
        query_requirements: dict[str, Any] | None = None,
    ) -> str:
        """
        Select appropriate OCR engine for a document.
        
        Args:
            document_url: URL or path to the document
            document_metadata: Optional document metadata
            query_requirements: Optional query requirements dictionary
            
        Returns:
            OCR engine name (e.g., "doctr", "easyocr", "paddleocr")
        """
        if not document_metadata:
            document_metadata = {}
        if not query_requirements:
            query_requirements = {}
        
        # Extract requirements
        layout_type = query_requirements.get("layout") or document_metadata.get("layout")
        handwriting_detected = query_requirements.get("handwriting_detected", False)
        heavy_pdf_or_image = query_requirements.get("heavy_pdf_or_image", False)
        region = query_requirements.get("region") or document_metadata.get("region")
        latency_requirement = query_requirements.get("latency_ms", 0)
        structured_json_required = query_requirements.get("structured_json_required", False)
        
        # Routing logic (in priority order)
        
        # Structured JSON required → Omniparser
        if structured_json_required:
            return "omniparser"
        
        # Table layout → DocTR
        if layout_type == "table":
            return "doctr"
        
        # Handwriting detected → EasyOCR
        if handwriting_detected:
            return "easyocr"
        
        # Heavy PDF or image → Google Vision API
        if heavy_pdf_or_image:
            return "google_vision"
        
        # EU region or latency requirement > 1s → PaddleOCR
        if region == "EU" or latency_requirement > 1000:
            return "paddleocr"
        
        # Default → Tesseract (fallback)
        return "tesseract"
    
    def create_job_from_storage(
        self,
        session: Session,
        storage_path: str,
        bucket: str = "ocr-documents",
        engine: str | None = None,
        document_metadata: dict[str, Any] | None = None,
        query_requirements: dict[str, Any] | None = None,
    ) -> OCRJob:
        """
        Create an OCR job from a file in Supabase Storage.
        
        Args:
            session: Database session
            storage_path: Path to file in Supabase Storage
            bucket: Storage bucket name (default: ocr-documents)
            engine: Optional engine name (auto-selected if not provided)
            document_metadata: Optional document metadata
            query_requirements: Optional query requirements
            
        Returns:
            OCRJob instance
        """
        from app.services.storage import default_storage_service
        
        # Get public URL or signed URL from storage
        try:
            # Try to get public URL first
            document_url = default_storage_service.get_public_url(bucket=bucket, file_path=storage_path)
        except Exception:
            # If public URL fails, generate signed URL
            try:
                document_url = default_storage_service.create_signed_url(
                    bucket=bucket,
                    file_path=storage_path,
                    expires_in=3600,  # 1 hour
                )
            except Exception as e:
                logger.error(f"Failed to get URL for storage file {bucket}/{storage_path}: {e}")
                raise OCRServiceError(f"Failed to access file in storage: {str(e)}")
        
        # Add storage info to metadata
        if not document_metadata:
            document_metadata = {}
        document_metadata["storage_bucket"] = bucket
        document_metadata["storage_path"] = storage_path
        
        # Create job using the URL
        return self.create_job(
            session=session,
            document_url=document_url,
            engine=engine,
            document_metadata=document_metadata,
            query_requirements=query_requirements,
        )
    
    def create_job(
        self,
        session: Session,
        document_url: str,
        engine: str | None = None,
        document_metadata: dict[str, Any] | None = None,
        query_requirements: dict[str, Any] | None = None,
    ) -> OCRJob:
        """
        Create a new OCR job.
        
        Args:
            session: Database session
            document_url: URL or path to the document
            engine: Optional engine name (auto-selected if not provided)
            document_metadata: Optional document metadata
            query_requirements: Optional query requirements
            
        Returns:
            OCRJob instance
        """
        # Select engine if not provided
        if not engine:
            engine = self.select_engine(
                document_url=document_url,
                document_metadata=document_metadata,
                query_requirements=query_requirements,
            )
        
        # Create job
        job = OCRJob(
            document_url=document_url,
            engine=engine,
            status="running",
            started_at=datetime.utcnow(),
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        
        # Create document record
        document = OCRDocument(
            job_id=job.id,
            file_url=document_url,
            file_type=self._detect_file_type(document_url),
            document_metadata=document_metadata or {},
        )
        session.add(document)
        session.commit()
        session.refresh(document)
        
        logger.info(f"Created OCR job: {job.id} (Engine: {engine}, Document: {document_url})")
        
        return job
    
    def process_job(
        self,
        session: Session,
        job_id: uuid.UUID,
    ) -> OCRResult:
        """
        Process an OCR job.
        
        Args:
            session: Database session
            job_id: OCR job ID
            
        Returns:
            OCRResult instance
        """
        job = session.get(OCRJob, job_id)
        if not job:
            raise JobNotFoundError(f"OCR job {job_id} not found")
        
        if job.status != "running":
            raise OCRServiceError(f"OCR job {job_id} is not in running status")
        
        # Get OCR engine client
        engine_client = self._get_engine_client(job.engine)
        
        # Execute OCR
        try:
            result_data = self._execute_ocr(
                client=engine_client,
                document_url=job.document_url,
                engine=job.engine,
            )
            
            # Create result record
            result = OCRResult(
                job_id=job.id,
                extracted_text=result_data.get("text", ""),
                structured_data=result_data.get("structured_data"),
                confidence_score=result_data.get("confidence_score"),
            )
            session.add(result)
            
            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.result = {
                "engine": job.engine,
                "text_length": len(result.extracted_text),
                "confidence_score": result.confidence_score,
            }
            session.add(job)
            session.commit()
            session.refresh(result)
            
            logger.info(f"OCR job {job_id} completed successfully (Engine: {job.engine})")
            
            return result
            
        except Exception as e:
            # Update job status to failed
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            session.add(job)
            session.commit()
            
            logger.error(f"OCR job {job_id} failed: {e}", exc_info=True)
            raise OCRServiceError(f"OCR processing failed: {e}")
    
    def get_job(
        self,
        session: Session,
        job_id: uuid.UUID,
    ) -> OCRJob:
        """
        Get OCR job by ID.
        
        Args:
            session: Database session
            job_id: Job ID
            
        Returns:
            OCRJob instance
        """
        job = session.get(OCRJob, job_id)
        if not job:
            raise JobNotFoundError(f"OCR job {job_id} not found")
        return job
    
    def get_job_result(
        self,
        session: Session,
        job_id: uuid.UUID,
    ) -> OCRResult | None:
        """
        Get OCR result for a job.
        
        Args:
            session: Database session
            job_id: Job ID
            
        Returns:
            OCRResult instance or None if not found
        """
        result = session.exec(
            select(OCRResult).where(OCRResult.job_id == job_id)
        ).first()
        return result
    
    def list_jobs(
        self,
        session: Session,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[OCRJob]:
        """
        List OCR jobs.
        
        Args:
            session: Database session
            status: Optional status filter
            skip: Skip count
            limit: Limit count
            
        Returns:
            List of OCRJob instances
        """
        statement = select(OCRJob)
        
        if status:
            statement = statement.where(OCRJob.status == status)
        
        statement = statement.order_by(OCRJob.started_at.desc()).offset(skip).limit(limit)
        
        jobs = session.exec(statement).all()
        return list(jobs)
    
    def _get_engine_client(self, engine: str) -> Any:
        """
        Get client for a specific OCR engine.
        
        Args:
            engine: OCR engine name
            
        Returns:
            OCR engine client
        """
        if engine not in self._ocr_engines:
            # Unknown engine - create placeholder
            self._ocr_engines[engine] = {
                "name": engine,
                "is_available": False,
            }
        
        client = self._ocr_engines[engine]
        
        if not client.get("is_available"):
            logger.warning(f"OCR engine '{engine}' not available. Falling back to Tesseract or placeholder.")
            # Try to fallback to Tesseract if available
            if self._ocr_engines.get("tesseract", {}).get("is_available"):
                return self._ocr_engines["tesseract"]
        
        return client
    
    def _execute_ocr(
        self,
        client: Any,
        document_url: str,
        engine: str,
    ) -> dict[str, Any]:
        """
        Execute OCR on a document using the specified engine.
        
        Args:
            client: OCR engine client
            document_url: Document URL or path
            engine: Engine name
            
        Returns:
            OCR result dictionary
        """
        if not client.get("is_available"):
            # Fallback to placeholder if engine not available
            return {
                "text": f"OCR engine '{engine}' not available. Please install required dependencies.",
                "structured_data": None,
                "confidence_score": 0.0,
            }
        
        try:
            # Download document if it's a URL
            image_data = self._load_document(document_url)
            
            if engine == "tesseract":
                return self._execute_tesseract(client["client"], image_data)
            elif engine == "easyocr":
                return self._execute_easyocr(client["client"], image_data)
            elif engine == "google_vision":
                return self._execute_google_vision(client["client"], image_data)
            else:
                # Unknown engine, try Tesseract as fallback
                if self._ocr_engines.get("tesseract", {}).get("is_available"):
                    logger.info(f"Unknown engine '{engine}', falling back to Tesseract")
                    return self._execute_tesseract(self._ocr_engines["tesseract"]["client"], image_data)
                else:
                    return {
                        "text": f"Unknown OCR engine '{engine}' and no fallback available",
                        "structured_data": None,
                        "confidence_score": 0.0,
                    }
        except Exception as e:
            logger.error(f"OCR execution failed for engine '{engine}': {e}", exc_info=True)
            return {
                "text": f"OCR execution failed: {str(e)}",
                "structured_data": None,
                "confidence_score": 0.0,
            }
    
    def _load_document(self, document_url: str) -> bytes:
        """
        Load document from URL or file path.
        
        Args:
            document_url: URL or file path
            
        Returns:
            Document data as bytes
        """
        if document_url.startswith(("http://", "https://")):
            # Download from URL
            response = urlopen(document_url, timeout=30)
            return response.read()
        else:
            # Read from file path
            with open(document_url, "rb") as f:
                return f.read()
    
    def _execute_tesseract(self, pytesseract_client: Any, image_data: bytes) -> dict[str, Any]:
        """Execute OCR using Tesseract."""
        try:
            from PIL import Image
            
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Perform OCR
            text = pytesseract_client.image_to_string(image)
            
            # Get confidence data (if available)
            try:
                data = pytesseract_client.image_to_data(image, output_type=pytesseract_client.Output.DICT)
                confidences = [int(conf) for conf in data["conf"] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.95
            except Exception:
                avg_confidence = 0.95
            
            return {
                "text": text.strip(),
                "structured_data": None,
                "confidence_score": avg_confidence,
            }
        except ImportError:
            return {
                "text": "PIL (Pillow) not installed. Install with: pip install Pillow",
                "structured_data": None,
                "confidence_score": 0.0,
            }
        except Exception as e:
            raise OCRServiceError(f"Tesseract OCR failed: {e}")
    
    def _execute_easyocr(self, reader: Any, image_data: bytes) -> dict[str, Any]:
        """Execute OCR using EasyOCR."""
        try:
            # EasyOCR expects image path or numpy array
            import numpy as np
            from PIL import Image
            
            # Convert bytes to PIL Image then to numpy array
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Perform OCR
            results = reader.readtext(image_array)
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            for (bbox, text, confidence) in results:
                text_parts.append(text)
                confidences.append(confidence)
            
            text = " ".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.95
            
            return {
                "text": text.strip(),
                "structured_data": {
                    "detections": [
                        {"text": text, "confidence": conf, "bbox": bbox}
                        for (bbox, text, conf) in results
                    ]
                },
                "confidence_score": avg_confidence,
            }
        except ImportError as e:
            return {
                "text": f"Required dependencies not installed: {e}",
                "structured_data": None,
                "confidence_score": 0.0,
            }
        except Exception as e:
            raise OCRServiceError(f"EasyOCR failed: {e}")
    
    def _execute_google_vision(self, client: Any, image_data: bytes) -> dict[str, Any]:
        """Execute OCR using Google Vision API."""
        try:
            from google.cloud import vision
            
            # Create image object
            image = vision.Image(content=image_data)
            
            # Perform text detection
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                # First text is the entire detected text
                full_text = texts[0].description
                
                # Calculate average confidence from all detections
                confidences = []
                for text in texts[1:]:  # Skip first (full text)
                    if hasattr(text, "confidence"):
                        confidences.append(text.confidence)
                
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.95
                
                # Extract structured data (bounding boxes)
                structured_data = {
                    "detections": [
                        {
                            "text": text.description,
                            "confidence": getattr(text, "confidence", None),
                            "bounding_poly": {
                                "vertices": [
                                    {"x": v.x, "y": v.y}
                                    for v in text.bounding_poly.vertices
                                ]
                            } if hasattr(text, "bounding_poly") else None,
                        }
                        for text in texts[1:]  # Skip first (full text)
                    ]
                }
                
                return {
                    "text": full_text.strip(),
                    "structured_data": structured_data,
                    "confidence_score": avg_confidence,
                }
            else:
                return {
                    "text": "",
                    "structured_data": None,
                    "confidence_score": 0.0,
                }
        except Exception as e:
            raise OCRServiceError(f"Google Vision API failed: {e}")
    
    def _detect_file_type(self, document_url: str) -> str:
        """
        Detect file type from URL or path.
        
        Args:
            document_url: Document URL or path
            
        Returns:
            File type (e.g., "pdf", "image", "png", "jpg")
        """
        # Extract extension
        if "." in document_url:
            extension = document_url.split(".")[-1].lower()
            
            # Map common extensions
            image_extensions = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"}
            if extension in image_extensions:
                return "image"
            elif extension == "pdf":
                return "pdf"
            else:
                return extension
        
        return "unknown"
    
    def initialize_engine_client(
        self,
        engine: str,
        config: dict[str, Any],
    ) -> None:
        """
        Initialize an OCR engine client.
        
        Args:
            engine: OCR engine name
            config: Client configuration
        """
        # Placeholder - will be implemented per OCR engine
        self._ocr_engines[engine] = {
            "name": engine,
            "config": config,
            "is_available": True,
        }
        logger.info(f"Initialized OCR engine client: {engine}")
    
    def batch_process(
        self,
        session: Session,
        document_urls: list[str],
        engine: str | None = None,
        document_metadata: dict[str, Any] | None = None,
        query_requirements: dict[str, Any] | None = None,
    ) -> list[OCRJob]:
        """
        Create multiple OCR jobs for batch processing.
        
        Args:
            session: Database session
            document_urls: List of document URLs
            engine: Optional engine name (auto-selected if not provided)
            document_metadata: Optional document metadata
            query_requirements: Optional query requirements
            
        Returns:
            List of OCRJob instances
        """
        jobs = []
        
        for document_url in document_urls:
            job = self.create_job(
                session=session,
                document_url=document_url,
                engine=engine,
                document_metadata=document_metadata,
                query_requirements=query_requirements,
            )
            jobs.append(job)
        
        logger.info(f"Created {len(jobs)} OCR jobs for batch processing")
        
        return jobs


# Default OCR service instance
default_ocr_service = OCRService()

