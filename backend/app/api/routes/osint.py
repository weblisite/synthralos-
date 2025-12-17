"""
OSINT API Routes

Endpoints for OSINT operations:
- POST /osint/stream - Create streaming OSINT query
- POST /osint/digest - Create batch OSINT query
- GET /osint/alerts - List OSINT alerts
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep
from app.models import OSINTAlert, OSINTStream, OSINTSignal
from app.osint.service import (
    OSINTServiceError,
    default_osint_service,
)

router = APIRouter(prefix="/osint", tags=["osint"])


# Request/Response Models
class StreamRequest(BaseModel):
    """Request model for creating OSINT stream."""
    platform: str = Field(..., description="Target platform (twitter, reddit, news, etc.)")
    keywords: list[str] = Field(..., description="List of keywords to monitor")
    engine: str | None = Field(None, description="Optional engine name (auto-selected if not provided)")
    requirements: dict[str, Any] | None = Field(None, description="Optional requirements dictionary")


class StreamResponse(BaseModel):
    """Response model for OSINT stream."""
    id: str
    platform: str
    keywords: list[str]
    engine: str
    is_active: bool
    created_at: str


class DigestRequest(BaseModel):
    """Request model for batch OSINT query."""
    platform: str = Field(..., description="Target platform")
    keywords: list[str] = Field(..., description="List of keywords to search")
    engine: str | None = Field(None, description="Optional engine name")
    requirements: dict[str, Any] | None = Field(None, description="Optional requirements dictionary")


class SignalResponse(BaseModel):
    """Response model for OSINT signal."""
    id: str
    stream_id: str
    source: str
    author: str | None
    text: str
    media: list[str]
    link: str | None
    sentiment_score: float | None
    created_at: str


class DigestResponse(BaseModel):
    """Response model for batch OSINT query."""
    stream_id: str
    signals: list[SignalResponse]
    total_count: int


class AlertResponse(BaseModel):
    """Response model for OSINT alert."""
    id: str
    stream_id: str | None
    alert_type: str
    message: str
    severity: str
    is_read: bool
    created_at: str


@router.post("/stream", status_code=status.HTTP_201_CREATED)
def create_stream(
    request: StreamRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamResponse:
    """
    Create a new OSINT stream for real-time monitoring.
    
    Creates a stream that continuously monitors a platform for keywords
    and collects signals (posts, tweets, articles, etc.).
    
    Request Body:
    - platform: Target platform (twitter, reddit, news, etc.)
    - keywords: List of keywords to monitor
    - engine: Optional engine name (auto-selected if not provided)
    - requirements: Optional requirements dictionary
    
    Returns:
    - Stream details with ID and status
    """
    osint_service = default_osint_service
    
    try:
        stream = osint_service.create_stream(
            session=session,
            platform=request.platform,
            keywords=request.keywords,
            engine=request.engine,
            requirements=request.requirements,
        )
        
        return StreamResponse(
            id=str(stream.id),
            platform=stream.platform,
            keywords=stream.keywords,
            engine=stream.engine,
            is_active=stream.is_active,
            created_at=stream.created_at.isoformat(),
        )
    except OSINTServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/digest", status_code=status.HTTP_200_OK)
def create_digest(
    request: DigestRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> DigestResponse:
    """
    Create a batch OSINT query (digest).
    
    Executes a one-time OSINT query and returns collected signals.
    This is useful for ad-hoc searches without continuous monitoring.
    
    Request Body:
    - platform: Target platform
    - keywords: List of keywords to search
    - engine: Optional engine name (auto-selected if not provided)
    - requirements: Optional requirements dictionary
    
    Returns:
    - List of signals collected from the query
    """
    osint_service = default_osint_service
    
    try:
        # Create a temporary stream for batch query
        stream = osint_service.create_stream(
            session=session,
            platform=request.platform,
            keywords=request.keywords,
            engine=request.engine,
            requirements=request.requirements,
        )
        
        # Execute stream to collect signals
        signals = osint_service.execute_stream(
            session=session,
            stream_id=str(stream.id),
        )
        
        # Deactivate stream after batch query
        stream.is_active = False
        session.add(stream)
        session.commit()
        
        return DigestResponse(
            stream_id=str(stream.id),
            signals=[
                SignalResponse(
                    id=str(signal.id),
                    stream_id=str(signal.stream_id),
                    source=signal.source,
                    author=signal.author,
                    text=signal.text,
                    media=signal.media,
                    link=signal.link,
                    sentiment_score=signal.sentiment_score,
                    created_at=signal.created_at.isoformat(),
                )
                for signal in signals
            ],
            total_count=len(signals),
        )
    except OSINTServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/streams", status_code=status.HTTP_200_OK)
def list_streams(
    session: SessionDep,
    current_user: CurrentUser,
    is_active: bool | None = Query(None, description="Filter by active status"),
    platform: str | None = Query(None, description="Filter by platform"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """
    List OSINT streams.
    
    Query Parameters:
    - is_active: Optional filter by active status
    - platform: Optional filter by platform
    - limit: Maximum number of streams to return (1-1000)
    - offset: Number of streams to skip
    
    Returns:
    - List of streams
    """
    query = select(OSINTStream)
    
    # Apply filters
    if is_active is not None:
        query = query.where(OSINTStream.is_active == is_active)
    
    if platform:
        query = query.where(OSINTStream.platform == platform)
    
    # Order by created_at descending
    query = query.order_by(OSINTStream.created_at.desc())
    
    # Apply pagination
    streams = session.exec(query.limit(limit).offset(offset)).all()
    
    return {
        "streams": [
            {
                "id": str(stream.id),
                "platform": stream.platform,
                "keywords": stream.keywords,
                "engine": stream.engine,
                "is_active": stream.is_active,
                "created_at": stream.created_at.isoformat(),
            }
            for stream in streams
        ],
        "total_count": len(streams),
    }


@router.get("/streams/{stream_id}/signals")
def get_stream_signals(
    stream_id: str,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """
    Get signals from an OSINT stream.
    
    Path Parameters:
    - stream_id: Stream ID
    
    Query Parameters:
    - limit: Maximum number of signals to return (1-1000)
    - offset: Number of signals to skip
    
    Returns:
    - List of signals from the stream
    """
    try:
        stream_uuid = uuid.UUID(stream_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stream ID: {stream_id}",
        )
    
    stream = session.get(OSINTStream, stream_uuid)
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSINT stream {stream_id} not found",
        )
    
    # Get signals
    signals = session.exec(
        select(OSINTSignal)
        .where(OSINTSignal.stream_id == stream_uuid)
        .order_by(OSINTSignal.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    
    return {
        "stream_id": str(stream.id),
        "platform": stream.platform,
        "keywords": stream.keywords,
        "signals": [
            {
                "id": str(signal.id),
                "source": signal.source,
                "author": signal.author,
                "text": signal.text,
                "media": signal.media,
                "link": signal.link,
                "sentiment_score": signal.sentiment_score,
                "created_at": signal.created_at.isoformat(),
            }
            for signal in signals
        ],
        "total_count": len(signals),
    }


@router.get("/alerts")
def list_alerts(
    session: SessionDep,
    current_user: CurrentUser,
    stream_id: str | None = Query(None, description="Filter by stream ID"),
    severity: str | None = Query(None, description="Filter by severity (low, medium, high, critical)"),
    is_read: bool | None = Query(None, description="Filter by read status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """
    List OSINT alerts.
    
    Query Parameters:
    - stream_id: Optional filter by stream ID
    - severity: Optional filter by severity
    - is_read: Optional filter by read status
    - limit: Maximum number of alerts to return (1-1000)
    - offset: Number of alerts to skip
    
    Returns:
    - List of alerts
    """
    query = select(OSINTAlert)
    
    # Apply filters
    if stream_id:
        try:
            stream_uuid = uuid.UUID(stream_id)
            query = query.where(OSINTAlert.stream_id == stream_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stream ID: {stream_id}",
            )
    
    if severity:
        query = query.where(OSINTAlert.severity == severity)
    
    if is_read is not None:
        query = query.where(OSINTAlert.is_read == is_read)
    
    # Order by created_at descending
    query = query.order_by(OSINTAlert.created_at.desc())
    
    # Apply pagination
    alerts = session.exec(query.limit(limit).offset(offset)).all()
    
    return {
        "alerts": [
            {
                "id": str(alert.id),
                "stream_id": str(alert.stream_id) if alert.stream_id else None,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "severity": alert.severity,
                "is_read": alert.is_read,
                "created_at": alert.created_at.isoformat(),
            }
            for alert in alerts
        ],
        "total_count": len(alerts),
    }


@router.post("/alerts/{alert_id}/read", status_code=status.HTTP_200_OK)
def mark_alert_read(
    alert_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """
    Mark an alert as read.
    
    Path Parameters:
    - alert_id: Alert ID
    
    Returns:
    - Updated alert details
    """
    try:
        alert_uuid = uuid.UUID(alert_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid alert ID: {alert_id}",
        )
    
    alert = session.get(OSINTAlert, alert_uuid)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSINT alert {alert_id} not found",
        )
    
    alert.is_read = True
    session.add(alert)
    session.commit()
    session.refresh(alert)
    
    return {
        "id": str(alert.id),
        "stream_id": str(alert.stream_id) if alert.stream_id else None,
        "alert_type": alert.alert_type,
        "message": alert.message,
        "severity": alert.severity,
        "is_read": alert.is_read,
        "created_at": alert.created_at.isoformat(),
    }


@router.post("/streams/{stream_id}/execute", status_code=status.HTTP_200_OK)
def execute_stream(
    stream_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """
    Execute an OSINT stream to collect signals.
    
    Path Parameters:
    - stream_id: Stream ID
    
    Returns:
    - List of collected signals
    """
    osint_service = default_osint_service
    
    try:
        signals = osint_service.execute_stream(
            session=session,
            stream_id=stream_id,
        )
        
        return {
            "stream_id": stream_id,
            "signals": [
                {
                    "id": str(signal.id),
                    "source": signal.source,
                    "author": signal.author,
                    "text": signal.text,
                    "media": signal.media,
                    "link": signal.link,
                    "sentiment_score": signal.sentiment_score,
                    "created_at": signal.created_at.isoformat(),
                }
                for signal in signals
            ],
            "total_count": len(signals),
        }
    except OSINTServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/streams/{stream_id}/status", status_code=status.HTTP_200_OK)
def update_stream_status(
    stream_id: str,
    session: SessionDep,
    current_user: CurrentUser,
    is_active: bool,
) -> StreamResponse:
    """
    Update stream active status.
    
    Path Parameters:
    - stream_id: Stream ID
    
    Request Body:
    - is_active: New active status
    
    Returns:
    - Updated stream details
    """
    try:
        stream_uuid = uuid.UUID(stream_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stream ID: {stream_id}",
        )
    
    stream = session.get(OSINTStream, stream_uuid)
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSINT stream {stream_id} not found",
        )
    
    stream.is_active = is_active
    session.add(stream)
    session.commit()
    session.refresh(stream)
    
    return StreamResponse(
        id=str(stream.id),
        platform=stream.platform,
        keywords=stream.keywords,
        engine=stream.engine,
        is_active=stream.is_active,
        created_at=stream.created_at.isoformat(),
    )

