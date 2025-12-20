"""
Code Execution Service

Multi-runtime code execution service with routing logic for:
- E2B (secure sandbox environments)
- WasmEdge (WebAssembly runtime)
- Bacalhau (distributed compute)
- Cline Node (AI-powered code execution)
- MCP Server (Model Context Protocol)
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app.models import CodeExecution, CodeSandbox

logger = logging.getLogger(__name__)


class CodeExecutionError(Exception):
    """Base exception for code execution errors."""

    pass


class RuntimeNotAvailableError(CodeExecutionError):
    """Code execution runtime not available."""

    pass


class ExecutionTimeoutError(CodeExecutionError):
    """Code execution timed out."""

    pass


class CodeExecutionService:
    """
    Code execution service for multi-runtime code execution.

    Routes code execution to appropriate runtime based on:
    - Language (Python, JavaScript, TypeScript, Bash, etc.)
    - Requirements (GPU, networking, file system, etc.)
    - Runtime availability
    - Resource constraints
    """

    def __init__(self):
        """Initialize code execution service."""
        self._runtimes: dict[str, Any] = {}
        self._initialize_runtimes()

    def _initialize_runtimes(self) -> None:
        """Initialize code execution runtimes."""
        # Placeholder for runtime initialization
        # Will be implemented per runtime
        self._runtimes = {
            "e2b": None,  # E2B runtime
            "wasmedge": None,  # WasmEdge runtime
            "bacalhau": None,  # Bacalhau runtime
            "cline_node": None,  # Cline Node runtime
            "mcp_server": None,  # MCP Server runtime
        }

    def select_runtime(
        self,
        language: str,
        requirements: dict[str, Any] | None = None,
    ) -> str:
        """
        Select appropriate runtime for code execution.

        Routing Logic:
        - language = python/javascript/typescript → E2B (general purpose)
        - language = wasm → WasmEdge
        - distributed_compute = true → Bacalhau
        - ai_guided = true → Cline Node
        - mcp_protocol = true → MCP Server
        - gpu_required = true → E2B (GPU support)
        - networking_required = true → E2B (network access)

        Args:
            language: Programming language
            requirements: Optional requirements dictionary

        Returns:
            Runtime name (e.g., "e2b", "wasmedge", "bacalhau")
        """
        if not requirements:
            requirements = {}

        # Check for explicit runtime preference
        preferred_runtime = requirements.get("runtime")
        if preferred_runtime and preferred_runtime in self._runtimes:
            return preferred_runtime

        # Routing logic based on language and requirements
        language_lower = language.lower()

        # WebAssembly → WasmEdge
        if language_lower == "wasm" or requirements.get("wasm", False):
            return "wasmedge"

        # Distributed compute → Bacalhau
        if requirements.get("distributed_compute", False):
            return "bacalhau"

        # AI-guided execution → Cline Node
        if requirements.get("ai_guided", False):
            return "cline_node"

        # MCP protocol → MCP Server
        if requirements.get("mcp_protocol", False):
            return "mcp_server"

        # Default to E2B for general purpose execution
        return "e2b"

    def create_execution(
        self,
        session: Session,
        code: str,
        language: str,
        runtime: str | None = None,
        input_data: dict[str, Any] | None = None,
        requirements: dict[str, Any] | None = None,
        timeout_seconds: int = 300,
    ) -> CodeExecution:
        """
        Create a new code execution.

        Args:
            session: Database session
            code: Code to execute
            language: Programming language
            runtime: Optional runtime name (auto-selected if not provided)
            input_data: Optional input data dictionary
            requirements: Optional requirements dictionary
            timeout_seconds: Execution timeout in seconds (default: 300)

        Returns:
            CodeExecution instance
        """
        # Select runtime if not provided
        if not runtime:
            runtime = self.select_runtime(language, requirements)

        # Create execution record
        execution = CodeExecution(
            runtime=runtime,
            language=language,
            code=code,
            input_data=input_data or {},
            status="running",
            started_at=datetime.utcnow(),
        )
        session.add(execution)
        session.commit()
        session.refresh(execution)

        logger.info(
            f"Created code execution: {execution.id} (Runtime: {runtime}, Language: {language})"
        )

        return execution

    def execute_code(
        self,
        session: Session,
        execution_id: str,
    ) -> CodeExecution:
        """
        Execute code using the specified runtime.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Updated CodeExecution instance

        Raises:
            CodeExecutionError: If execution fails
        """
        # Get execution
        execution = session.get(CodeExecution, execution_id)
        if not execution:
            raise CodeExecutionError(f"Code execution {execution_id} not found")

        if execution.status != "running":
            raise CodeExecutionError(
                f"Code execution {execution_id} is not in running status"
            )

        try:
            # Get runtime handler
            runtime_handler = self._get_runtime_handler(execution.runtime)

            # Execute code using runtime
            start_time = datetime.utcnow()
            result = self._execute_with_runtime(
                runtime_handler,
                execution.code,
                execution.language,
                execution.input_data,
                execution.runtime,
            )

            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Update execution with result
            execution.status = "completed"
            execution.output_data = result
            execution.completed_at = end_time
            execution.duration_ms = duration_ms
            execution.exit_code = result.get("exit_code", 0)
            execution.memory_mb = result.get("memory_mb")
            session.add(execution)
            session.commit()
            session.refresh(execution)

            logger.info(
                f"Executed code: {execution_id} (Duration: {duration_ms}ms, Exit Code: {execution.exit_code})"
            )

            return execution

        except ExecutionTimeoutError as e:
            # Update execution with timeout error
            execution.status = "failed"
            execution.error_message = f"Execution timeout: {str(e)}"
            execution.completed_at = datetime.utcnow()
            session.add(execution)
            session.commit()

            logger.error(f"Code execution timeout: {execution_id}")
            raise CodeExecutionError(f"Execution timeout: {e}")

        except Exception as e:
            # Update execution with error
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            session.add(execution)
            session.commit()

            logger.error(f"Code execution failed: {execution_id}", exc_info=True)
            raise CodeExecutionError(f"Execution failed: {e}")

    def create_sandbox(
        self,
        session: Session,
        name: str,
        runtime: str,
        config: dict[str, Any] | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> CodeSandbox:
        """
        Create a persistent code sandbox environment.

        Args:
            session: Database session
            name: Sandbox name
            runtime: Runtime name
            config: Optional sandbox configuration
            owner_id: Optional owner ID

        Returns:
            CodeSandbox instance
        """
        # Create sandbox record
        sandbox = CodeSandbox(
            name=name,
            runtime=runtime,
            config=config or {},
            owner_id=owner_id or uuid.uuid4(),  # TODO: Get from current user
        )
        session.add(sandbox)
        session.commit()
        session.refresh(sandbox)

        logger.info(
            f"Created code sandbox: {sandbox.id} (Runtime: {runtime}, Name: {name})"
        )

        return sandbox

    def execute_in_sandbox(
        self,
        session: Session,
        sandbox_id: str,
        code: str,
        language: str,
        input_data: dict[str, Any] | None = None,
    ) -> CodeExecution:
        """
        Execute code in a persistent sandbox environment.

        Args:
            session: Database session
            sandbox_id: Sandbox ID
            code: Code to execute
            language: Programming language
            input_data: Optional input data dictionary

        Returns:
            CodeExecution instance
        """
        # Get sandbox
        sandbox = session.get(CodeSandbox, sandbox_id)
        if not sandbox:
            raise CodeExecutionError(f"Code sandbox {sandbox_id} not found")

        # Create execution in sandbox
        execution = self.create_execution(
            session=session,
            code=code,
            language=language,
            runtime=sandbox.runtime,
            input_data=input_data,
            requirements=sandbox.config,
        )

        # Execute code
        return self.execute_code(session, str(execution.id))

    def _get_runtime_handler(self, runtime: str) -> Any:
        """
        Get handler for a specific runtime.

        Args:
            runtime: Runtime name

        Returns:
            Runtime handler instance

        Raises:
            RuntimeNotAvailableError: If runtime not found
        """
        if runtime not in self._runtimes:
            raise RuntimeNotAvailableError(f"Runtime '{runtime}' not found")

        handler = self._runtimes[runtime]
        if handler is None:
            raise RuntimeNotAvailableError(f"Runtime '{runtime}' not available")

        return handler

    def _execute_with_runtime(
        self,
        handler: Any,
        code: str,
        language: str,
        input_data: dict[str, Any],
        runtime: str,
    ) -> dict[str, Any]:
        """
        Execute code using runtime handler.

        Args:
            handler: Runtime handler instance
            code: Code to execute
            language: Programming language
            input_data: Input data dictionary
            runtime: Runtime name

        Returns:
            Result data dictionary
        """
        # Execute code using subprocess (basic implementation)
        # For production, use E2B, WasmEdge, or other secure sandboxed runtimes
        return self._execute_with_subprocess(code, language, input_data, runtime)

    def _execute_with_subprocess(
        self,
        code: str,
        language: str,
        input_data: dict[str, Any],
        runtime: str,
    ) -> dict[str, Any]:
        """
        Execute code using subprocess (basic implementation).

        WARNING: This is a basic implementation. For production, use secure sandboxed runtimes
        like E2B, WasmEdge, or Bacalhau.

        Args:
            code: Code to execute
            language: Programming language
            input_data: Input data dictionary
            runtime: Runtime name

        Returns:
            Result data dictionary
        """
        import json
        import os
        import resource
        import subprocess
        import tempfile

        from app.core.config import settings

        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=self._get_file_extension(language)
            ) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Determine command based on language
                cmd = self._get_execution_command(language, temp_file)

                if not cmd:
                    return {
                        "output": f"Unsupported language: {language}",
                        "exit_code": 1,
                        "memory_mb": None,
                        "stdout": "",
                        "stderr": f"Language '{language}' is not supported",
                        "result": None,
                    }

                # Set timeout
                timeout = input_data.get("timeout", settings.CODE_EXECUTION_TIMEOUT)

                # Execute code
                start_memory = (
                    resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
                )  # KB to MB

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    cwd=tempfile.gettempdir(),
                )

                # Send input data as JSON to stdin if provided
                stdin_data = (
                    json.dumps(input_data.get("input", {}))
                    if input_data.get("input")
                    else None
                )

                try:
                    stdout, stderr = process.communicate(
                        input=stdin_data, timeout=timeout
                    )
                    exit_code = process.returncode
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    exit_code = -1
                    stderr = f"Execution timeout after {timeout} seconds\n{stderr}"

                end_memory = (
                    resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
                )
                memory_mb = max(0, end_memory - start_memory)

                # Try to parse output as JSON if possible
                result = None
                try:
                    result = json.loads(stdout.strip())
                except (json.JSONDecodeError, ValueError):
                    pass

                return {
                    "output": stdout,
                    "exit_code": exit_code,
                    "memory_mb": round(memory_mb, 2),
                    "stdout": stdout,
                    "stderr": stderr,
                    "result": result,
                }
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Code execution failed: {e}", exc_info=True)
            return {
                "output": "",
                "exit_code": 1,
                "memory_mb": None,
                "stdout": "",
                "stderr": str(e),
                "result": None,
            }

    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "bash": ".sh",
            "shell": ".sh",
            "ruby": ".rb",
            "php": ".php",
            "go": ".go",
            "rust": ".rs",
            "java": ".java",
        }
        return extensions.get(language.lower(), ".txt")

    def _get_execution_command(self, language: str, file_path: str) -> list[str] | None:
        """Get execution command for language."""
        commands = {
            "python": ["python3", file_path],
            "python3": ["python3", file_path],
            "javascript": ["node", file_path],
            "node": ["node", file_path],
            "bash": ["bash", file_path],
            "shell": ["bash", file_path],
            "ruby": ["ruby", file_path],
            "php": ["php", file_path],
        }
        return commands.get(language.lower())


# Default code execution service instance
default_code_execution_service = CodeExecutionService()
