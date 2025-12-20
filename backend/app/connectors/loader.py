"""
Connector Hot-Loader Service

Handles isolated loading of connector wheels, method invocation, and version pinning.
Provides secure execution environment for connectors.
"""

import importlib
import importlib.util
import logging
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from app.models import ConnectorVersion

logger = logging.getLogger(__name__)


class ConnectorLoaderError(Exception):
    """Base exception for connector loader errors."""

    pass


class WheelLoadError(ConnectorLoaderError):
    """Failed to load connector wheel."""

    pass


class MethodNotFoundError(ConnectorLoaderError):
    """Connector method not found."""

    pass


class ConnectorHotLoader:
    """
    Hot-loader for connector wheels.

    Features:
    - Isolated wheel loading (separate module namespace)
    - Version pinning (loads specific connector version)
    - Method invocation (calls connector actions/triggers)
    - Security isolation (prevents connector code from affecting main app)
    """

    def __init__(self):
        """Initialize connector hot-loader."""
        self._loaded_modules: dict[str, Any] = {}  # version_id -> module
        self._temp_dirs: dict[str, Path] = {}  # version_id -> temp_dir

    def load_connector(
        self,
        connector_version: ConnectorVersion,
        force_reload: bool = False,
    ) -> Any:
        """
        Load a connector wheel into an isolated module namespace.

        Args:
            connector_version: ConnectorVersion instance
            force_reload: Force reload even if already loaded

        Returns:
            Loaded connector module

        Raises:
            WheelLoadError: If wheel cannot be loaded
        """
        version_id = str(connector_version.id)

        # Check if already loaded
        if version_id in self._loaded_modules and not force_reload:
            logger.debug(
                f"Connector {version_id} already loaded, returning cached module"
            )
            return self._loaded_modules[version_id]

        # Download and extract wheel if URL provided
        if connector_version.wheel_url:
            module = self._load_from_wheel(connector_version)
        else:
            # If no wheel URL, assume connector is installed as a package
            # Try to import using slug
            manifest = connector_version.manifest
            slug = manifest.get("slug", "")
            package_name = manifest.get("package_name", slug)

            try:
                module = importlib.import_module(package_name)
                logger.info(
                    f"Loaded connector '{slug}' from installed package '{package_name}'"
                )
            except ImportError as e:
                raise WheelLoadError(
                    f"Connector '{slug}' not found as installed package '{package_name}': {e}"
                )

        # Cache the loaded module
        self._loaded_modules[version_id] = module

        return module

    def _load_from_wheel(self, connector_version: ConnectorVersion) -> Any:
        """
        Download and load connector from wheel URL.

        Args:
            connector_version: ConnectorVersion instance

        Returns:
            Loaded connector module
        """
        wheel_url = connector_version.wheel_url
        if not wheel_url:
            raise WheelLoadError("No wheel URL provided")

        manifest = connector_version.manifest
        slug = manifest.get("slug", "")
        package_name = manifest.get("package_name", slug)

        # Create temporary directory for this version
        temp_dir = tempfile.mkdtemp(prefix=f"connector_{slug}_")
        self._temp_dirs[str(connector_version.id)] = Path(temp_dir)

        try:
            # Download wheel file
            logger.info(f"Downloading connector wheel from {wheel_url}")
            wheel_path = self._download_wheel(wheel_url, temp_dir)

            # Extract wheel
            logger.info(f"Extracting connector wheel to {temp_dir}")
            self._extract_wheel(wheel_path, temp_dir)

            # Load module from extracted wheel
            module = self._load_module_from_path(temp_dir, package_name)

            logger.info(
                f"Successfully loaded connector '{slug}' version {connector_version.version}"
            )
            return module

        except Exception as e:
            logger.error(f"Failed to load connector wheel: {e}")
            raise WheelLoadError(f"Failed to load connector wheel: {e}")

    def _download_wheel(self, url: str, dest_dir: Path) -> Path:
        """
        Download wheel file from URL.

        Args:
            url: Wheel file URL
            dest_dir: Destination directory

        Returns:
            Path to downloaded wheel file
        """
        parsed_url = urlparse(url)
        filename = parsed_url.path.split("/")[-1] or "connector.whl"
        wheel_path = dest_dir / filename

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()

            with open(wheel_path, "wb") as f:
                f.write(response.content)

        logger.debug(f"Downloaded wheel to {wheel_path}")
        return wheel_path

    def _extract_wheel(self, wheel_path: Path, dest_dir: Path) -> None:
        """
        Extract wheel file.

        Args:
            wheel_path: Path to wheel file
            dest_dir: Destination directory
        """
        with zipfile.ZipFile(wheel_path, "r") as zip_ref:
            zip_ref.extractall(dest_dir)

        logger.debug(f"Extracted wheel to {dest_dir}")

    def _load_module_from_path(self, module_path: Path, package_name: str) -> Any:
        """
        Load Python module from a file path.

        Args:
            module_path: Path to module directory
            package_name: Package name to import

        Returns:
            Loaded module
        """
        # Add module path to sys.path temporarily
        module_path_str = str(module_path)
        if module_path_str not in sys.path:
            sys.path.insert(0, module_path_str)

        try:
            # Import the module
            module = importlib.import_module(package_name)
            return module
        except ImportError:
            # Try to find and load the main module file
            # Look for __init__.py or {package_name}.py
            init_file = module_path / package_name / "__init__.py"
            main_file = module_path / f"{package_name}.py"

            if init_file.exists():
                spec = importlib.util.spec_from_file_location(package_name, init_file)
            elif main_file.exists():
                spec = importlib.util.spec_from_file_location(package_name, main_file)
            else:
                raise WheelLoadError(
                    f"Could not find module file for '{package_name}' in {module_path}"
                )

            if spec is None or spec.loader is None:
                raise WheelLoadError(
                    f"Could not create module spec for '{package_name}'"
                )

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return module

    def invoke_method(
        self,
        connector_version: ConnectorVersion,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Invoke a method on a connector.

        Args:
            connector_version: ConnectorVersion instance
            method_name: Method name to invoke
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Method return value

        Raises:
            MethodNotFoundError: If method not found
            ConnectorLoaderError: If invocation fails
        """
        # Load connector module
        module = self.load_connector(connector_version)

        # Get method from module
        if not hasattr(module, method_name):
            raise MethodNotFoundError(
                f"Method '{method_name}' not found in connector '{connector_version.manifest.get('slug')}'"
            )

        method = getattr(module, method_name)

        if not callable(method):
            raise MethodNotFoundError(
                f"'{method_name}' is not callable in connector '{connector_version.manifest.get('slug')}'"
            )

        # Invoke method
        try:
            logger.info(
                f"Invoking method '{method_name}' on connector '{connector_version.manifest.get('slug')}'"
            )
            result = method(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error invoking method '{method_name}': {e}")
            raise ConnectorLoaderError(f"Method invocation failed: {e}")

    def invoke_action(
        self,
        connector_version: ConnectorVersion,
        action_id: str,
        input_data: dict[str, Any],
        credentials: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Invoke a connector action.

        Args:
            connector_version: ConnectorVersion instance
            action_id: Action ID from manifest
            input_data: Action input data
            credentials: Optional credentials (will be injected from Infisical if not provided)

        Returns:
            Action output data
        """
        manifest = connector_version.manifest
        actions = manifest.get("actions", {})

        if action_id not in actions:
            raise MethodNotFoundError(
                f"Action '{action_id}' not found in connector '{manifest.get('slug')}'"
            )

        action_config = actions[action_id]
        method_name = action_config.get("method", action_id)

        # Prepare arguments
        # Connectors typically expect (credentials, input_data) or just (input_data,)
        if credentials:
            result = self.invoke_method(
                connector_version, method_name, credentials, input_data
            )
        else:
            result = self.invoke_method(connector_version, method_name, input_data)

        # Ensure result is a dictionary
        if not isinstance(result, dict):
            result = {"result": result}

        return result

    def invoke_trigger(
        self,
        connector_version: ConnectorVersion,
        trigger_id: str,
        input_data: dict[str, Any],
        credentials: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Invoke a connector trigger.

        Args:
            connector_version: ConnectorVersion instance
            trigger_id: Trigger ID from manifest
            input_data: Trigger input data
            credentials: Optional credentials

        Returns:
            Trigger output data
        """
        manifest = connector_version.manifest
        triggers = manifest.get("triggers", {})

        if trigger_id not in triggers:
            raise MethodNotFoundError(
                f"Trigger '{trigger_id}' not found in connector '{manifest.get('slug')}'"
            )

        trigger_config = triggers[trigger_id]
        method_name = trigger_config.get("method", trigger_id)

        # Prepare arguments
        if credentials:
            result = self.invoke_method(
                connector_version, method_name, credentials, input_data
            )
        else:
            result = self.invoke_method(connector_version, method_name, input_data)

        # Ensure result is a dictionary
        if not isinstance(result, dict):
            result = {"result": result}

        return result

    def unload_connector(self, version_id: str) -> None:
        """
        Unload a connector and clean up resources.

        Args:
            version_id: Connector version ID
        """
        # Remove from cache
        if version_id in self._loaded_modules:
            del self._loaded_modules[version_id]

        # Clean up temp directory
        if version_id in self._temp_dirs:
            temp_dir = self._temp_dirs[version_id]
            import shutil

            try:
                shutil.rmtree(temp_dir)
                logger.debug(
                    f"Cleaned up temp directory for connector version {version_id}"
                )
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")
            del self._temp_dirs[version_id]

    def clear_cache(self) -> None:
        """Clear all loaded connectors and temp directories."""
        version_ids = list(self._loaded_modules.keys())
        for version_id in version_ids:
            self.unload_connector(version_id)

        logger.info("Cleared connector loader cache")


# Default connector loader instance
default_connector_loader = ConnectorHotLoader()
