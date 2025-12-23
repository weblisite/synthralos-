"""
Workflow Dependencies

Manages workflow-to-workflow dependencies:
- Dependency graph validation
- Dependency-based execution order
- Circular dependency detection
"""

import uuid

from sqlmodel import Session

from app.models import Workflow


class DependencyError(Exception):
    """Base exception for dependency errors."""

    pass


class DependencyManager:
    """
    Manages workflow dependencies.
    """

    def __init__(self):
        """Initialize dependency manager."""
        pass

    def get_workflow_dependencies(
        self,
        session: Session,
        workflow_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        """
        Get dependencies for a workflow.

        Args:
            session: Database session
            workflow_id: Workflow ID

        Returns:
            List of dependent workflow IDs
        """
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            return []

        # Get dependencies from graph_config
        graph_config = workflow.graph_config or {}
        dependencies = graph_config.get("dependencies", [])

        # Convert string UUIDs to UUID objects
        dependency_ids = []
        for dep_id in dependencies:
            try:
                if isinstance(dep_id, str):
                    dependency_ids.append(uuid.UUID(dep_id))
                else:
                    dependency_ids.append(dep_id)
            except ValueError:
                continue

        return dependency_ids

    def add_dependency(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        depends_on_workflow_id: uuid.UUID,
    ) -> None:
        """
        Add a dependency to a workflow.

        Args:
            session: Database session
            workflow_id: Workflow ID
            depends_on_workflow_id: Workflow ID to depend on

        Raises:
            DependencyError: If circular dependency detected
        """
        # Check for circular dependency
        if self._check_circular_dependency(
            session, workflow_id, depends_on_workflow_id
        ):
            raise DependencyError(
                f"Circular dependency detected: {workflow_id} -> {depends_on_workflow_id}"
            )

        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise DependencyError(f"Workflow {workflow_id} not found")

        graph_config = workflow.graph_config or {}
        dependencies = graph_config.get("dependencies", [])

        # Add dependency if not already present
        dep_id_str = str(depends_on_workflow_id)
        if dep_id_str not in dependencies:
            dependencies.append(dep_id_str)
            graph_config["dependencies"] = dependencies
            workflow.graph_config = graph_config

            session.add(workflow)
            session.commit()

    def remove_dependency(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        depends_on_workflow_id: uuid.UUID,
    ) -> None:
        """
        Remove a dependency from a workflow.

        Args:
            session: Database session
            workflow_id: Workflow ID
            depends_on_workflow_id: Workflow ID to remove dependency on
        """
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            return

        graph_config = workflow.graph_config or {}
        dependencies = graph_config.get("dependencies", [])

        dep_id_str = str(depends_on_workflow_id)
        if dep_id_str in dependencies:
            dependencies.remove(dep_id_str)
            graph_config["dependencies"] = dependencies
            workflow.graph_config = graph_config

            session.add(workflow)
            session.commit()

    def validate_dependency_graph(
        self,
        session: Session,
        workflow_id: uuid.UUID,
    ) -> tuple[bool, list[str]]:
        """
        Validate dependency graph for a workflow.

        Args:
            session: Database session
            workflow_id: Workflow ID

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Check for circular dependencies
        if self._has_circular_dependency(session, workflow_id):
            errors.append(f"Circular dependency detected for workflow {workflow_id}")

        # Check if all dependencies exist
        dependencies = self.get_workflow_dependencies(session, workflow_id)
        for dep_id in dependencies:
            dep_workflow = session.get(Workflow, dep_id)
            if not dep_workflow:
                errors.append(f"Dependency {dep_id} not found")

        return (len(errors) == 0, errors)

    def get_execution_order(
        self,
        session: Session,
        workflow_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        """
        Get execution order for workflows based on dependencies.

        Args:
            session: Database session
            workflow_ids: List of workflow IDs

        Returns:
            List of workflow IDs in execution order
        """
        # Build dependency graph
        graph: dict[uuid.UUID, set[uuid.UUID]] = {}
        for workflow_id in workflow_ids:
            graph[workflow_id] = set(
                self.get_workflow_dependencies(session, workflow_id)
            )

        # Topological sort
        ordered: list[uuid.UUID] = []
        visited: set[uuid.UUID] = set()
        temp_visited: set[uuid.UUID] = set()

        def visit(node: uuid.UUID) -> None:
            if node in temp_visited:
                raise DependencyError("Circular dependency detected")
            if node in visited:
                return

            temp_visited.add(node)
            for dep in graph.get(node, set()):
                if dep in workflow_ids:  # Only consider dependencies in the list
                    visit(dep)

            temp_visited.remove(node)
            visited.add(node)
            ordered.append(node)

        for workflow_id in workflow_ids:
            if workflow_id not in visited:
                visit(workflow_id)

        return ordered

    def _check_circular_dependency(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        depends_on_workflow_id: uuid.UUID,
    ) -> bool:
        """
        Check if adding a dependency would create a circular dependency.

        Args:
            session: Database session
            workflow_id: Workflow ID
            depends_on_workflow_id: Workflow ID to depend on

        Returns:
            True if circular dependency would be created
        """
        # Check if depends_on_workflow_id depends on workflow_id (directly or indirectly)
        visited: set[uuid.UUID] = set()

        def check_depends_on(target: uuid.UUID, check_for: uuid.UUID) -> bool:
            if target == check_for:
                return True

            if target in visited:
                return False

            visited.add(target)
            dependencies = self.get_workflow_dependencies(session, target)

            for dep_id in dependencies:
                if check_depends_on(dep_id, check_for):
                    return True

            return False

        return check_depends_on(depends_on_workflow_id, workflow_id)

    def _has_circular_dependency(
        self,
        session: Session,
        workflow_id: uuid.UUID,
    ) -> bool:
        """
        Check if workflow has circular dependencies.

        Args:
            session: Database session
            workflow_id: Workflow ID

        Returns:
            True if circular dependency exists
        """
        visited: set[uuid.UUID] = set()
        rec_stack: set[uuid.UUID] = set()

        def has_cycle(node: uuid.UUID) -> bool:
            visited.add(node)
            rec_stack.add(node)

            dependencies = self.get_workflow_dependencies(session, node)
            for dep_id in dependencies:
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        return has_cycle(workflow_id)


# Default dependency manager instance
default_dependency_manager = DependencyManager()
