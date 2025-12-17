"""
Code API Routes

Endpoints for code execution and tool registry:
- POST /code/execute - Execute code
- POST /code/register-tool - Register code tool
- GET /code/tools - List code tools
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep
from app.code.registry import (
    CodeToolRegistryError,
    InvalidToolError,
    InvalidVersionError,
    ToolNotFoundError,
    ToolValidationError,
    default_code_tool_registry,
)
from app.code.service import (
    CodeExecutionError,
    ExecutionTimeoutError,
    RuntimeNotAvailableError,
    default_code_execution_service,
)
from app.models import CodeExecution, CodeSandbox, CodeToolRegistry

router = APIRouter(prefix="/code", tags=["code"])


# Request/Response Models
class ExecuteCodeRequest(BaseModel):
    """Request model for code execution."""
    code: str = Field(..., description="Code to execute")
    language: str = Field(..., description="Programming language (python, javascript, typescript, bash)")
    runtime: str | None = Field(None, description="Optional runtime name (auto-selected if not provided)")
    input_data: dict[str, Any] | None = Field(None, description="Optional input data dictionary")
    requirements: dict[str, Any] | None = Field(None, description="Optional requirements dictionary")
    timeout_seconds: int = Field(300, ge=1, le=3600, description="Execution timeout in seconds")


class ExecuteCodeResponse(BaseModel):
    """Response model for code execution."""
    id: str
    runtime: str
    language: str
    status: str
    exit_code: int | None
    duration_ms: int
    memory_mb: int | None
    output_data: dict[str, Any] | None
    error_message: str | None
    started_at: str
    completed_at: str | None


class RegisterToolRequest(BaseModel):
    """Request model for tool registration."""
    tool_id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Tool name")
    version: str = Field(..., description="SemVer version string (e.g., 1.0.0)")
    code: str = Field(..., description="Tool code")
    runtime: str = Field(..., description="Runtime name (e2b, wasmedge, bacalhau, etc.)")
    description: str | None = Field(None, description="Optional tool description")
    input_schema: dict[str, Any] | None = Field(None, description="Optional input schema (Pydantic or Zod)")
    output_schema: dict[str, Any] | None = Field(None, description="Optional output schema (Pydantic or Zod)")


class ToolResponse(BaseModel):
    """Response model for code tool."""
    id: str
    tool_id: str
    name: str
    version: str
    description: str | None
    runtime: str
    usage_count: int
    is_deprecated: bool
    created_at: str
    updated_at: str


class SandboxRequest(BaseModel):
    """Request model for sandbox creation."""
    name: str = Field(..., description="Sandbox name")
    runtime: str = Field(..., description="Runtime name")
    config: dict[str, Any] | None = Field(None, description="Optional sandbox configuration")


class SandboxResponse(BaseModel):
    """Response model for sandbox."""
    id: str
    name: str
    runtime: str
    config: dict[str, Any]
    created_at: str


@router.post("/execute", status_code=status.HTTP_201_CREATED)
def execute_code(
    request: ExecuteCodeRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> ExecuteCodeResponse:
    """
    Execute code in a secure sandbox environment.
    
    Creates a code execution and runs it using the specified runtime.
    Supports multiple runtimes: E2B, WasmEdge, Bacalhau, Cline Node, MCP Server.
    
    Request Body:
    - code: Code to execute
    - language: Programming language
    - runtime: Optional runtime name (auto-selected if not provided)
    - input_data: Optional input data dictionary
    - requirements: Optional requirements dictionary
    - timeout_seconds: Execution timeout (default: 300 seconds)
    
    Returns:
    - Execution details with output data or error message
    """
    code_service = default_code_execution_service
    
    try:
        # Create execution
        execution = code_service.create_execution(
            session=session,
            code=request.code,
            language=request.language,
            runtime=request.runtime,
            input_data=request.input_data,
            requirements=request.requirements,
            timeout_seconds=request.timeout_seconds,
        )
        
        # Execute code
        execution = code_service.execute_code(session, str(execution.id))
        
        return ExecuteCodeResponse(
            id=str(execution.id),
            runtime=execution.runtime,
            language=execution.language,
            status=execution.status,
            exit_code=execution.exit_code,
            duration_ms=execution.duration_ms,
            memory_mb=execution.memory_mb,
            output_data=execution.output_data,
            error_message=execution.error_message,
            started_at=execution.started_at.isoformat(),
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
        )
    except RuntimeNotAvailableError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Runtime not available: {str(e)}",
        )
    except ExecutionTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Execution timeout: {str(e)}",
        )
    except CodeExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/execute/{execution_id}")
def get_execution_status(
    execution_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> ExecuteCodeResponse:
    """
    Get code execution status.
    
    Path Parameters:
    - execution_id: Execution ID
    
    Returns:
    - Execution details with current status
    """
    try:
        execution_uuid = uuid.UUID(execution_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid execution ID: {execution_id}",
        )
    
    execution = session.get(CodeExecution, execution_uuid)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Code execution {execution_id} not found",
        )
    
    return ExecuteCodeResponse(
        id=str(execution.id),
        runtime=execution.runtime,
        language=execution.language,
        status=execution.status,
        exit_code=execution.exit_code,
        duration_ms=execution.duration_ms,
        memory_mb=execution.memory_mb,
        output_data=execution.output_data,
        error_message=execution.error_message,
        started_at=execution.started_at.isoformat(),
        completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
    )


@router.post("/register-tool", status_code=status.HTTP_201_CREATED)
def register_tool(
    request: RegisterToolRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> ToolResponse:
    """
    Register a new code tool or new version of existing tool.
    
    Tools can be registered with input/output schemas for validation.
    Supports Pydantic schemas for Python tools and Zod schemas for JavaScript/TypeScript tools.
    
    Request Body:
    - tool_id: Unique tool identifier
    - name: Tool name
    - version: SemVer version string
    - code: Tool code
    - runtime: Runtime name
    - description: Optional tool description
    - input_schema: Optional input schema (Pydantic or Zod)
    - output_schema: Optional output schema (Pydantic or Zod)
    
    Returns:
    - Registered tool details
    """
    registry = default_code_tool_registry
    
    try:
        tool = registry.register_tool(
            session=session,
            tool_id=request.tool_id,
            name=request.name,
            version=request.version,
            code=request.code,
            runtime=request.runtime,
            description=request.description,
            input_schema=request.input_schema,
            output_schema=request.output_schema,
            owner_id=current_user.id,
        )
        
        return ToolResponse(
            id=str(tool.id),
            tool_id=tool.tool_id,
            name=tool.name,
            version=tool.version,
            description=tool.description,
            runtime=tool.runtime,
            usage_count=tool.usage_count,
            is_deprecated=tool.is_deprecated,
            created_at=tool.created_at.isoformat(),
            updated_at=tool.updated_at.isoformat(),
        )
    except InvalidToolError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InvalidVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ToolValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/tools")
def list_tools(
    session: SessionDep,
    current_user: CurrentUser,
    runtime: str | None = Query(None, description="Filter by runtime"),
    owner_id: str | None = Query(None, description="Filter by owner ID"),
    include_deprecated: bool = Query(False, description="Include deprecated tools"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """
    List registered code tools.
    
    Query Parameters:
    - runtime: Optional filter by runtime
    - owner_id: Optional filter by owner ID
    - include_deprecated: Include deprecated tools (default: false)
    - limit: Maximum number of tools to return (1-1000)
    - offset: Number of tools to skip
    
    Returns:
    - List of tools with metadata
    """
    registry = default_code_tool_registry
    
    owner_uuid = None
    if owner_id:
        try:
            owner_uuid = uuid.UUID(owner_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid owner ID: {owner_id}",
            )
    
    tools = registry.list_tools(
        session=session,
        runtime=runtime,
        owner_id=owner_uuid,
        include_deprecated=include_deprecated,
    )
    
    # Apply pagination
    paginated_tools = tools[offset:offset + limit]
    
    return {
        "tools": [
            {
                "id": str(tool.id),
                "tool_id": tool.tool_id,
                "name": tool.name,
                "version": tool.version,
                "description": tool.description,
                "runtime": tool.runtime,
                "usage_count": tool.usage_count,
                "is_deprecated": tool.is_deprecated,
                "created_at": tool.created_at.isoformat(),
                "updated_at": tool.updated_at.isoformat(),
            }
            for tool in paginated_tools
        ],
        "total_count": len(tools),
        "limit": limit,
        "offset": offset,
    }


@router.get("/tools/{tool_id}")
def get_tool(
    tool_id: str,
    session: SessionDep,
    current_user: CurrentUser,
    version: str | None = Query(None, description="Tool version (uses latest if not provided)"),
) -> dict[str, Any]:
    """
    Get code tool details.
    
    Path Parameters:
    - tool_id: Tool ID
    
    Query Parameters:
    - version: Optional version string (uses latest if not provided)
    
    Returns:
    - Tool details including code and schemas
    """
    registry = default_code_tool_registry
    
    try:
        tool = registry.get_tool(
            session=session,
            tool_id=tool_id,
            version=version,
        )
        
        return {
            "id": str(tool.id),
            "tool_id": tool.tool_id,
            "name": tool.name,
            "version": tool.version,
            "description": tool.description,
            "code": tool.code,
            "runtime": tool.runtime,
            "input_schema": tool.input_schema,
            "output_schema": tool.output_schema,
            "usage_count": tool.usage_count,
            "is_deprecated": tool.is_deprecated,
            "created_at": tool.created_at.isoformat(),
            "updated_at": tool.updated_at.isoformat(),
        }
    except ToolNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/tools/{tool_id}/versions")
def get_tool_versions(
    tool_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """
    Get all versions of a tool.
    
    Path Parameters:
    - tool_id: Tool ID
    
    Returns:
    - List of all tool versions
    """
    registry = default_code_tool_registry
    
    try:
        versions = registry.get_tool_versions(
            session=session,
            tool_id=tool_id,
        )
        
        return {
            "tool_id": tool_id,
            "versions": [
                {
                    "id": str(version.id),
                    "version": version.version,
                    "is_deprecated": version.is_deprecated,
                    "usage_count": version.usage_count,
                    "created_at": version.created_at.isoformat(),
                    "updated_at": version.updated_at.isoformat(),
                }
                for version in versions
            ],
            "total_count": len(versions),
        }
    except ToolNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/tools/{tool_id}/deprecate", status_code=status.HTTP_200_OK)
def deprecate_tool(
    tool_id: str,
    session: SessionDep,
    current_user: CurrentUser,
    version: str | None = Query(None, description="Tool version (deprecates all versions if not provided)"),
) -> ToolResponse:
    """
    Deprecate a tool or specific version.
    
    Path Parameters:
    - tool_id: Tool ID
    
    Query Parameters:
    - version: Optional version (deprecates all versions if not provided)
    
    Returns:
    - Updated tool details
    """
    registry = default_code_tool_registry
    
    try:
        tool = registry.deprecate_tool(
            session=session,
            tool_id=tool_id,
            version=version,
        )
        
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_id}' not found",
            )
        
        return ToolResponse(
            id=str(tool.id),
            tool_id=tool.tool_id,
            name=tool.name,
            version=tool.version,
            description=tool.description,
            runtime=tool.runtime,
            usage_count=tool.usage_count,
            is_deprecated=tool.is_deprecated,
            created_at=tool.created_at.isoformat(),
            updated_at=tool.updated_at.isoformat(),
        )
    except ToolNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/sandboxes", status_code=status.HTTP_200_OK)
def list_sandboxes(
    session: SessionDep,
    current_user: CurrentUser,
    runtime: str | None = Query(None, description="Filter by runtime"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[SandboxResponse]:
    """
    List code sandboxes for the current user.
    
    Query Parameters:
    - runtime: Optional filter by runtime
    - limit: Maximum number of sandboxes to return (1-1000)
    - offset: Number of sandboxes to skip
    
    Returns:
    - List of sandboxes
    """
    from sqlmodel import select
    
    query = select(CodeSandbox).where(CodeSandbox.owner_id == current_user.id)
    
    if runtime:
        query = query.where(CodeSandbox.runtime == runtime)
    
    query = query.order_by(CodeSandbox.created_at.desc()).limit(limit).offset(offset)
    
    sandboxes = session.exec(query).all()
    
    return [
        SandboxResponse(
            id=str(sandbox.id),
            name=sandbox.name,
            runtime=sandbox.runtime,
            config=sandbox.config,
            created_at=sandbox.created_at.isoformat(),
        )
        for sandbox in sandboxes
    ]


@router.post("/sandbox", status_code=status.HTTP_201_CREATED)
def create_sandbox(
    request: SandboxRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> SandboxResponse:
    """
    Create a persistent code sandbox environment.
    
    Sandboxes allow for persistent state across multiple code executions.
    
    Request Body:
    - name: Sandbox name
    - runtime: Runtime name
    - config: Optional sandbox configuration
    
    Returns:
    - Sandbox details
    """
    code_service = default_code_execution_service
    
    try:
        sandbox = code_service.create_sandbox(
            session=session,
            name=request.name,
            runtime=request.runtime,
            config=request.config,
            owner_id=current_user.id,
        )
        
        return SandboxResponse(
            id=str(sandbox.id),
            name=sandbox.name,
            runtime=sandbox.runtime,
            config=sandbox.config,
            created_at=sandbox.created_at.isoformat(),
        )
    except CodeExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/sandbox/{sandbox_id}/execute", status_code=status.HTTP_201_CREATED)
def execute_in_sandbox(
    sandbox_id: str,
    request: ExecuteCodeRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> ExecuteCodeResponse:
    """
    Execute code in a persistent sandbox environment.
    
    Path Parameters:
    - sandbox_id: Sandbox ID
    
    Request Body:
    - code: Code to execute
    - language: Programming language
    - input_data: Optional input data dictionary
    
    Returns:
    - Execution details
    """
    code_service = default_code_execution_service
    
    try:
        execution = code_service.execute_in_sandbox(
            session=session,
            sandbox_id=sandbox_id,
            code=request.code,
            language=request.language,
            input_data=request.input_data,
        )
        
        return ExecuteCodeResponse(
            id=str(execution.id),
            runtime=execution.runtime,
            language=execution.language,
            status=execution.status,
            exit_code=execution.exit_code,
            duration_ms=execution.duration_ms,
            memory_mb=execution.memory_mb,
            output_data=execution.output_data,
            error_message=execution.error_message,
            started_at=execution.started_at.isoformat(),
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
        )
    except CodeExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

