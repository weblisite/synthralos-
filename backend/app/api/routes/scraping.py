"""
Scraping API Routes

API endpoints for web scraping operations.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, HttpUrl

from app.api.deps import CurrentUser, SessionDep
from app.scraping.service import JobNotFoundError, ScrapingService, ScrapingServiceError

router = APIRouter(prefix="/scraping", tags=["scraping"])


# Request/Response Models
class ScrapeRequest(BaseModel):
    url: HttpUrl
    engine: str | None = None
    proxy_id: str | None = None
    auto_select_proxy: bool = True
    scrape_requirements: dict[str, Any] | None = None


class CrawlRequest(BaseModel):
    urls: list[HttpUrl]
    engine: str | None = None
    proxy_id: str | None = None
    scrape_requirements: dict[str, Any] | None = None


class ScrapeJobResponse(BaseModel):
    id: str
    url: str
    engine: str
    proxy_id: str | None
    status: str
    started_at: str
    completed_at: str | None
    error_message: str | None
    result: dict[str, Any] | None


class ScrapeResultResponse(BaseModel):
    id: str
    job_id: str
    content: str
    html: str | None
    result_metadata: dict[str, Any]
    created_at: str


class ScrapeStatusResponse(BaseModel):
    job: ScrapeJobResponse
    result: ScrapeResultResponse | None


@router.post("/scrape", status_code=status.HTTP_201_CREATED)
def create_scrape_job(
    request: ScrapeRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> ScrapeJobResponse:
    """
    Create a new scraping job for a single URL.

    Args:
        request: Scrape request with URL and optional parameters
        current_user: Current authenticated user
        db: Database session

    Returns:
        ScrapeJobResponse with job details
    """
    scraping_service = ScrapingService()

    try:
        job = scraping_service.create_job(
            session=session,
            url=str(request.url),
            engine=request.engine,
            proxy_id=request.proxy_id,
            scrape_requirements=request.scrape_requirements,
            auto_select_proxy=request.auto_select_proxy,
        )

        return ScrapeJobResponse(
            id=str(job.id),
            url=job.url,
            engine=job.engine,
            proxy_id=job.proxy_id,
            status=job.status,
            started_at=job.started_at.isoformat(),
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            error_message=job.error_message,
            result=job.result,
        )
    except ScrapingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/crawl", status_code=status.HTTP_201_CREATED)
def create_crawl_jobs(
    request: CrawlRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> list[ScrapeJobResponse]:
    """
    Create multiple scraping jobs for multi-page crawling.

    Args:
        request: Crawl request with list of URLs
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of ScrapeJobResponse with job details
    """
    scraping_service = ScrapingService()

    try:
        jobs = scraping_service.crawl_multiple_pages(
            session=session,
            urls=[str(url) for url in request.urls],
            engine=request.engine,
            proxy_id=request.proxy_id,
            scrape_requirements=request.scrape_requirements,
        )

        return [
            ScrapeJobResponse(
                id=str(job.id),
                url=job.url,
                engine=job.engine,
                proxy_id=job.proxy_id,
                status=job.status,
                started_at=job.started_at.isoformat(),
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
                error_message=job.error_message,
                result=job.result,
            )
            for job in jobs
        ]
    except ScrapingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/status/{job_id}", status_code=status.HTTP_200_OK)
def get_scrape_status(
    job_id: str,
    current_user: CurrentUser,
    session: SessionDep,
) -> ScrapeStatusResponse:
    """
    Get the status of a scraping job and its result if available.

    Args:
        job_id: Scraping job ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        ScrapeStatusResponse with job status and result
    """
    scraping_service = ScrapingService()

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID: {job_id}",
        )

    try:
        job = scraping_service.get_job(session=session, job_id=job_uuid)
        result = scraping_service.get_job_result(session=session, job_id=job_uuid)

        job_response = ScrapeJobResponse(
            id=str(job.id),
            url=job.url,
            engine=job.engine,
            proxy_id=job.proxy_id,
            status=job.status,
            started_at=job.started_at.isoformat(),
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            error_message=job.error_message,
            result=job.result,
        )

        result_response = None
        if result:
            result_response = ScrapeResultResponse(
                id=str(result.id),
                job_id=str(result.job_id),
                content=result.content,
                html=result.html,
                result_metadata=result.result_metadata,
                created_at=result.created_at.isoformat(),
            )

        return ScrapeStatusResponse(
            job=job_response,
            result=result_response,
        )
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ScrapingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/process/{job_id}", status_code=status.HTTP_200_OK)
def process_scrape_job(
    job_id: str,
    current_user: CurrentUser,
    session: SessionDep,
) -> ScrapeResultResponse:
    """
    Process a scraping job (execute the scraping).

    Args:
        job_id: Scraping job ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        ScrapeResultResponse with scraping result
    """
    scraping_service = ScrapingService()

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID: {job_id}",
        )

    try:
        result = scraping_service.process_job(session=session, job_id=job_uuid)

        return ScrapeResultResponse(
            id=str(result.id),
            job_id=str(result.job_id),
            content=result.content,
            html=result.html,
            result_metadata=result.result_metadata,
            created_at=result.created_at.isoformat(),
        )
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ScrapingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/jobs", status_code=status.HTTP_200_OK)
def list_scrape_jobs(
    *,
    current_user: CurrentUser,
    session: SessionDep,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[ScrapeJobResponse]:
    """
    List scraping jobs with optional status filter.

    Args:
        status: Optional status filter (running, completed, failed)
        skip: Skip count for pagination
        limit: Limit count for pagination
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of ScrapeJobResponse
    """
    scraping_service = ScrapingService()

    try:
        jobs = scraping_service.list_jobs(
            session=session,
            status=status,
            skip=skip,
            limit=limit,
        )

        return [
            ScrapeJobResponse(
                id=str(job.id),
                url=job.url,
                engine=job.engine,
                proxy_id=job.proxy_id,
                status=job.status,
                started_at=job.started_at.isoformat(),
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
                error_message=job.error_message,
                result=job.result,
            )
            for job in jobs
        ]
    except ScrapingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/change-detection", status_code=status.HTTP_201_CREATED)
def monitor_page_changes(
    session: SessionDep,
    current_user: CurrentUser,
    url: str = Body(...),
    check_interval_seconds: int = Body(
        3600, ge=60, le=86400
    ),  # Default 1 hour, min 1 min, max 24 hours
    selector: str | None = Body(
        None
    ),  # Optional CSS selector to monitor specific element
    notification_webhook: str | None = Body(
        None
    ),  # Optional webhook URL for notifications
) -> Any:
    """
    Monitor a page for changes.

    Creates a change detection record and schedules periodic checks.

    Request Body:
    - url: URL to monitor
    - check_interval_seconds: Interval between checks (60-86400 seconds)
    - selector: Optional CSS selector to monitor specific element
    - notification_webhook: Optional webhook URL for change notifications

    Returns:
    - Change detection record
    """
    import hashlib

    from app.models import ChangeDetection

    # Create initial change detection record
    # First, scrape the page to get baseline content
    scraping_service = ScrapingService()

    try:
        # Create a scrape job to get initial content
        scrape_job = scraping_service.create_job(
            session=session,
            url=url,
            engine="beautifulsoup",  # Use simple engine for change detection
            scrape_requirements={"simple_html": True},
        )

        # Process the job to get content
        result = scraping_service.process_job(session=session, job_id=scrape_job.id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get initial page content",
            )

        # Extract content (use selector if provided)
        content = result.content
        if selector and result.html:
            # TODO: Parse HTML and extract content by selector
            # For now, use full content
            content = result.content

        # Calculate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Create change detection record
        change_detection = ChangeDetection(
            url=url,
            diff_hash=content_hash,
            current_content=content,
            previous_content=None,  # No previous content on first check
        )
        session.add(change_detection)
        session.commit()
        session.refresh(change_detection)

        # TODO: Schedule periodic checks (would use a scheduler service)
        # For now, this creates the record and returns it

        return {
            "id": str(change_detection.id),
            "url": url,
            "check_interval_seconds": check_interval_seconds,
            "selector": selector,
            "notification_webhook": notification_webhook,
            "baseline_hash": content_hash,
            "created_at": change_detection.detected_at.isoformat(),
            "note": "Change detection monitoring started. Periodic checks will be scheduled.",
        }

    except ScrapingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize change detection: {str(e)}",
        )
