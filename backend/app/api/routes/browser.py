"""
Browser API Routes

API endpoints for browser automation operations.
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl
from app.api.deps import CurrentUser, SessionDep
from app.browser.service import BrowserService, BrowserServiceError, SessionNotFoundError

router = APIRouter(prefix="/browser", tags=["browser"])


# Request/Response Models
class BrowserSessionCreateRequest(BaseModel):
    browser_tool: str | None = None
    proxy_id: str | None = None
    auto_select_proxy: bool = True
    automation_requirements: dict[str, Any] | None = None


class BrowserActionRequest(BaseModel):
    action_type: str  # navigate, click, fill, screenshot, etc.
    action_data: dict[str, Any]


class BrowserMonitorRequest(BaseModel):
    url: HttpUrl
    check_interval_seconds: int = 60
    previous_content: str | None = None


class BrowserSessionResponse(BaseModel):
    id: str
    session_id: str
    browser_tool: str
    proxy_id: str | None
    status: str
    started_at: str
    closed_at: str | None
    error_message: str | None


class BrowserActionResponse(BaseModel):
    id: str
    session_id: str
    action_type: str
    action_data: dict[str, Any]
    result: dict[str, Any] | None
    timestamp: str


class BrowserSessionDetailResponse(BaseModel):
    session: BrowserSessionResponse
    actions: list[BrowserActionResponse]
    total_actions: int


class ChangeDetectionResponse(BaseModel):
    id: str
    url: str
    diff_hash: str
    previous_content: str | None
    current_content: str | None
    detected_at: str
    change_type: str | None
    description: str | None


@router.post("/session", status_code=status.HTTP_201_CREATED)
def create_browser_session(
    request: BrowserSessionCreateRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> BrowserSessionResponse:
    """
    Create a new browser session.
    
    Args:
        request: Browser session creation request
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        BrowserSessionResponse with session details
    """
    browser_service = BrowserService()
    
    try:
        browser_session = browser_service.create_session(
            session=session,
            browser_tool=request.browser_tool,
            proxy_id=request.proxy_id,
            automation_requirements=request.automation_requirements,
            auto_select_proxy=request.auto_select_proxy,
        )
        
        return BrowserSessionResponse(
            id=str(browser_session.id),
            session_id=browser_session.session_id,
            browser_tool=browser_session.browser_tool,
            proxy_id=browser_session.proxy_id,
            status=browser_session.status,
            started_at=browser_session.started_at.isoformat(),
            closed_at=browser_session.closed_at.isoformat() if browser_session.closed_at else None,
            error_message=browser_session.error_message,
        )
    except BrowserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/execute/{session_id}", status_code=status.HTTP_200_OK)
def execute_browser_action(
    session_id: str,
    request: BrowserActionRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> BrowserActionResponse:
    """
    Execute a browser action.
    
    Args:
        session_id: Browser session ID
        request: Browser action request
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        BrowserActionResponse with action result
    """
    browser_service = BrowserService()
    
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid session ID: {session_id}",
        )
    
    try:
        browser_action = browser_service.execute_action(
            session=session,
            session_id=session_uuid,
            action_type=request.action_type,
            action_data=request.action_data,
        )
        
        return BrowserActionResponse(
            id=str(browser_action.id),
            session_id=str(browser_action.session_id),
            action_type=browser_action.action_type,
            action_data=browser_action.action_data,
            result=browser_action.result,
            timestamp=browser_action.timestamp.isoformat(),
        )
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except BrowserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/session/{session_id}", status_code=status.HTTP_200_OK)
def get_browser_session(
    *,
    session_id: str,
    current_user: CurrentUser,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> BrowserSessionDetailResponse:
    """
    Get browser session details including actions.
    
    Args:
        session_id: Browser session ID
        skip: Skip count for actions pagination
        limit: Limit count for actions pagination
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        BrowserSessionDetailResponse with session and actions
    """
    browser_service = BrowserService()
    
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid session ID: {session_id}",
        )
    
    try:
        browser_session = browser_service.get_session(
            session=session,
            session_id=session_uuid,
        )
        
        actions = browser_service.get_session_actions(
            session=session,
            session_id=session_uuid,
            skip=skip,
            limit=limit,
        )
        
        session_response = BrowserSessionResponse(
            id=str(browser_session.id),
            session_id=browser_session.session_id,
            browser_tool=browser_session.browser_tool,
            proxy_id=browser_session.proxy_id,
            status=browser_session.status,
            started_at=browser_session.started_at.isoformat(),
            closed_at=browser_session.closed_at.isoformat() if browser_session.closed_at else None,
            error_message=browser_session.error_message,
        )
        
        actions_response = [
            BrowserActionResponse(
                id=str(action.id),
                session_id=str(action.session_id),
                action_type=action.action_type,
                action_data=action.action_data,
                result=action.result,
                timestamp=action.timestamp.isoformat(),
            )
            for action in actions
        ]
        
        return BrowserSessionDetailResponse(
            session=session_response,
            actions=actions_response,
            total_actions=len(actions_response),
        )
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except BrowserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/sessions", status_code=status.HTTP_200_OK)
def list_browser_sessions(
    *,
    current_user: CurrentUser,
    session: SessionDep,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[BrowserSessionResponse]:
    """
    List browser sessions with optional status filter.
    
    Args:
        status: Optional status filter (active, closed, error)
        skip: Skip count for pagination
        limit: Limit count for pagination
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        List of BrowserSessionResponse
    """
    browser_service = BrowserService()
    
    try:
        sessions = browser_service.list_sessions(
            session=session,
            status=status,
            skip=skip,
            limit=limit,
        )
        
        return [
            BrowserSessionResponse(
                id=str(browser_session.id),
                session_id=browser_session.session_id,
                browser_tool=browser_session.browser_tool,
                proxy_id=browser_session.proxy_id,
                status=browser_session.status,
                started_at=browser_session.started_at.isoformat(),
                closed_at=browser_session.closed_at.isoformat() if browser_session.closed_at else None,
                error_message=browser_session.error_message,
            )
            for browser_session in sessions
        ]
    except BrowserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/session/{session_id}/close", status_code=status.HTTP_200_OK)
def close_browser_session(
    session_id: str,
    current_user: CurrentUser,
    session: SessionDep,
) -> BrowserSessionResponse:
    """
    Close a browser session.
    
    Args:
        session_id: Browser session ID
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        BrowserSessionResponse with closed session details
    """
    browser_service = BrowserService()
    
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid session ID: {session_id}",
        )
    
    try:
        browser_session = browser_service.close_session(
            session=session,
            session_id=session_uuid,
        )
        
        return BrowserSessionResponse(
            id=str(browser_session.id),
            session_id=browser_session.session_id,
            browser_tool=browser_session.browser_tool,
            proxy_id=browser_session.proxy_id,
            status=browser_session.status,
            started_at=browser_session.started_at.isoformat(),
            closed_at=browser_session.closed_at.isoformat() if browser_session.closed_at else None,
            error_message=browser_session.error_message,
        )
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except BrowserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/monitor", status_code=status.HTTP_200_OK)
def monitor_page_changes(
    request: BrowserMonitorRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> ChangeDetectionResponse | None:
    """
    Monitor a page for changes.
    
    Args:
        request: Monitor request with URL and interval
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        ChangeDetectionResponse if changes detected, None otherwise
    """
    browser_service = BrowserService()
    
    try:
        change_detection = browser_service.monitor_page_changes(
            session=session,
            url=str(request.url),
            check_interval_seconds=request.check_interval_seconds,
            previous_content=request.previous_content,
        )
        
        if not change_detection:
            return None
        
        return ChangeDetectionResponse(
            id=str(change_detection.id),
            url=change_detection.url,
            diff_hash=change_detection.diff_hash,
            previous_content=change_detection.previous_content,
            current_content=change_detection.current_content,
            detected_at=change_detection.detected_at.isoformat(),
            change_type=change_detection.change_type,
            description=change_detection.description,
        )
    except BrowserServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

