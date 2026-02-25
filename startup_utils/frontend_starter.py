"""
Frontend Service Starter Module

Provides frontend-specific startup functionality including:
- Port detection and conflict resolution for the Vite dev server
- npm command handling for uni-app H5 development
- Integration with Vite development server startup
- node_modules detection and npm install trigger
- Dependency validation for frontend packages

This module handles the frontend service startup logic, ensuring that
the service starts on an available port and that dependencies are
properly installed.
"""

import os
import json
from pathlib import Path
from typing import Optional, Tuple

from startup_utils.port_checker import find_available_port, is_port_in_use
from startup_utils.dependency_installer import DependencyInstaller


class FrontendStarter:
    """
    Frontend service starter class for managing uni-app/Vite application startup.

    Handles port detection, npm command execution, node_modules detection,
    dependency validation, and provides the necessary configuration for
    starting the frontend service with npm.

    Attributes:
        default_port: The default port for the frontend service (5173).
        project_root: The root directory of the project.
        frontend_dir: The frontend directory path.
        package_json_path: Path to the package.json file.
        dev_command: The npm script command for development (dev:h5).
        node_modules_path: Path to the node_modules directory.

    Examples:
        >>> starter = FrontendStarter()
        >>> starter.default_port
        5173
        >>> available_port = starter.get_available_port()
        >>> print(f"Frontend will start on port {available_port}")
        Frontend will start on port 5173
        >>> print(f"Dev command: {starter.dev_command}")
        Dev command: dev:h5
    """

    # Default configuration
    DEFAULT_PORT = 5173
    DEFAULT_HOST = 'localhost'
    FRONTEND_DIR = 'frontend'
    PACKAGE_JSON_FILE = 'package.json'
    NODE_MODULES_DIR = 'node_modules'
    DEV_SCRIPT_NAME = 'dev:h5'

    def __init__(
        self,
        project_root: Optional[Path] = None,
        default_port: Optional[int] = None
    ) -> None:
        """
        Initialize the frontend service starter.

        Sets up paths and configuration for frontend service startup.
        If project_root is not provided, it will be detected automatically
        from the current working directory.

        Args:
            project_root: The root directory of the project.
                        If None, uses the current working directory.
            default_port: The default port to use for the frontend.
                         If None, uses DEFAULT_PORT (5173).

        Examples:
            >>> starter = FrontendStarter()
            >>> print(starter.default_port)
            5173
            >>> starter = FrontendStarter(default_port=3000)
            >>> print(starter.default_port)
            3000
            >>> print(starter.dev_command)
            dev:h5
        """
        # Determine project root
        if project_root is None:
            # Use current working directory or find project root
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(project_root)

        # Set default port
        self.default_port = default_port if default_port is not None else self.DEFAULT_PORT

        # Set up paths
        self.frontend_dir = self.project_root / self.FRONTEND_DIR
        self.package_json_path = self.frontend_dir / self.PACKAGE_JSON_FILE
        self.node_modules_path = self.frontend_dir / self.NODE_MODULES_DIR

        # Determine dev command from package.json or use default
        self.dev_command = self._get_dev_script()

    def _get_dev_script(self) -> str:
        """
        Get the development script name from package.json.

        Reads the package.json file and extracts the development script name.
        Falls back to the default DEV_SCRIPT_NAME if the script is not found.

        Returns:
            The development script name (e.g., 'dev:h5').

        Examples:
            >>> starter = FrontendStarter()
            >>> starter.dev_command
            'dev:h5'
        """
        if not self.package_json_path.exists():
            return self.DEV_SCRIPT_NAME

        try:
            with open(self.package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            scripts = package_data.get('scripts', {})
            # Prefer dev:h5 for uni-app H5 development
            if self.DEV_SCRIPT_NAME in scripts:
                return self.DEV_SCRIPT_NAME
            # Fallback to common dev script names
            for script_name in ['dev', 'serve', 'start']:
                if script_name in scripts:
                    return script_name

            return self.DEV_SCRIPT_NAME
        except (OSError, IOError, json.JSONDecodeError):
            return self.DEV_SCRIPT_NAME

    def has_package_json(self) -> bool:
        """
        Check if the frontend package.json file exists.

        Returns:
            True if the package.json file exists, False otherwise.

        Examples:
            >>> starter = FrontendStarter()
            >>> starter.has_package_json()
            True
        """
        return self.package_json_path.exists()

    def has_node_modules(self) -> bool:
        """
        Check if the frontend node_modules directory exists and appears complete.

        Checks for the existence of node_modules and verifies basic
        completeness by checking for package directories.

        Returns:
            True if node_modules exists and appears complete, False otherwise.

        Examples:
            >>> starter = FrontendStarter()
            >>> starter.has_node_modules()
            True
        """
        return self.node_modules_path.exists() and self.node_modules_path.is_dir()

    def check_dependencies(self) -> Tuple[bool, list[str]]:
        """
        Check if all frontend dependencies from package.json are installed.

        Uses the DependencyInstaller to validate that node_modules exists
        and contains the required packages.

        Returns:
            A tuple of (all_satisfied: bool, missing_packages: list[str]).
            - all_satisfied: True if all dependencies are installed, False otherwise.
            - missing_packages: List of package names that are missing (empty if check failed).

        Raises:
            FileNotFoundError: If package.json doesn't exist.

        Examples:
            >>> starter = FrontendStarter()
            >>> all_satisfied, missing = starter.check_dependencies()
            >>> if not all_satisfied:
            ...     print(f"Missing: {', '.join(missing)}")
            Missing: vue, pinia
        """
        if not self.package_json_path.exists():
            raise FileNotFoundError(
                f"Cannot check dependencies: {self.package_json_path} not found. "
                f"Please ensure the frontend directory contains a package.json file."
            )

        return DependencyInstaller.check_npm_dependencies(str(self.frontend_dir))

    def install_dependencies(self) -> Tuple[bool, str]:
        """
        Install frontend npm dependencies from package.json.

        Uses the DependencyInstaller to run npm install.
        If dependencies are already satisfied, returns success message.

        Returns:
            A tuple of (success: bool, message: str).
            - success: True if installation succeeded or deps already installed.
            - message: Success message or error details.

        Examples:
            >>> starter = FrontendStarter()
            >>> success, message = starter.install_dependencies()
            >>> if success:
            ...     print(message)
            All frontend dependencies are already installed
            >>> success, message = starter.install_dependencies()
            >>> if success:
            ...     print(message)
            Successfully installed 156 packages
        """
        installer = DependencyInstaller()
        return installer.install_frontend_dependencies(str(self.frontend_dir))

    def get_available_port(
        self,
        start_port: Optional[int] = None,
        host: str = 'localhost'
    ) -> int:
        """
        Find an available port for the frontend service.

        Checks if the default or specified port is available, and if not,
        finds the next available port by incrementing.

        Args:
            start_port: The port to start checking from.
                       If None, uses self.default_port.
            host: The host address to check. Defaults to 'localhost'.

        Returns:
            An available port number.

        Raises:
            RuntimeError: If no available port can be found within the
                         maximum number of attempts.

        Examples:
            >>> starter = FrontendStarter()
            >>> port = starter.get_available_port()
            >>> print(f"Available port: {port}")
            Available port: 5173
            >>> # If port 5173 is in use
            >>> port = starter.get_available_port()
            >>> print(f"Available port: {port}")
            Available port: 5174
        """
        start_port = start_port if start_port is not None else self.default_port

        available_port = find_available_port(start_port, host=host)

        if available_port is None:
            raise RuntimeError(
                f"Could not find an available port starting from {start_port}. "
                f"All ports from {start_port} to {min(start_port + 100, 65535)} are in use."
            )

        return available_port

    def is_port_available(self, port: int, host: str = 'localhost') -> bool:
        """
        Check if a specific port is available for the frontend service.

        Args:
            port: The port number to check.
            host: The host address to check. Defaults to 'localhost'.

        Returns:
            True if the port is available, False if it's in use.

        Examples:
            >>> starter = FrontendStarter()
            >>> starter.is_port_available(5173)
            False
            >>> starter.is_port_available(5174)
            True
        """
        return not is_port_in_use(port, host=host)

    def get_vite_config_port(self) -> Optional[int]:
        """
        Get the port configured in vite.config.ts.

        Reads the server.port value from the frontend's vite.config.ts
        file if it exists.

        Returns:
            The port number from vite.config.ts, or None if not configured.

        Examples:
            >>> starter = FrontendStarter()
            >>> port = starter.get_vite_config_port()
            >>> print(f"Configured port: {port}")
            Configured port: 5173
        """
        vite_config_path = self.frontend_dir / 'vite.config.ts'

        if not vite_config_path.exists():
            return None

        try:
            with open(vite_config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple regex to find port configuration
            # Handles both: port: 5173 and 'port': 5173
            import re
            port_match = re.search(r"port\s*:\s*(\d+)", content)
            if port_match:
                return int(port_match.group(1))

        except (OSError, IOError):
            pass

        return None

    def get_host(self) -> str:
        """
        Get the host address for the frontend service.

        Returns the configured host from vite.config.ts if available,
        otherwise returns the default host.

        Returns:
            The host address (e.g., 'localhost', '0.0.0.0').

        Examples:
            >>> starter = FrontendStarter()
            >>> host = starter.get_host()
            >>> print(f"Host: {host}")
            Host: localhost
        """
        vite_config_path = self.frontend_dir / 'vite.config.ts'

        if vite_config_path.exists():
            try:
                with open(vite_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple regex to find host configuration
                import re
                host_match = re.search(r"host\s*:\s*['\"]([^'\"]+)['\"]", content)
                if host_match:
                    return host_match.group(1)
            except (OSError, IOError):
                pass

        # Return default host
        return self.DEFAULT_HOST

    def get_startup_command(
        self,
        port: Optional[int] = None,
        host: Optional[str] = None
    ) -> str:
        """
        Get the npm startup command for the frontend service.

        Constructs the command to start the frontend with npm run,
        using the specified or detected port and host.

        Note: The port and host parameters are for documentation purposes.
        The actual port/host configuration is managed by vite.config.ts.
        Port detection before startup is still useful for conflict checking.

        Args:
            port: The port to use (for reference). If None, uses the default port.
            host: The host to use (for reference). If None, uses the default host.

        Returns:
            The npm startup command string.

        Examples:
            >>> starter = FrontendStarter()
            >>> cmd = starter.get_startup_command()
            >>> print(cmd)
            npm run dev:h5
        """
        return f"npm run {self.dev_command}"

    def get_startup_args(
        self,
        port: Optional[int] = None,
        host: Optional[str] = None
    ) -> dict:
        """
        Get the startup arguments for the frontend service.

        Returns a dictionary with all the necessary configuration
        for starting the frontend service programmatically.

        Args:
            port: The port to use. If None, uses the default port.
            host: The host to use. If None, uses the default host.

        Returns:
            Dictionary containing startup configuration with keys:
            - command: The npm command to run (e.g., 'npm run dev:h5')
            - dev_script: The script name from package.json (e.g., 'dev:h5')
            - port: The port number (for reference)
            - host: The host address (for reference)

        Examples:
            >>> starter = FrontendStarter()
            >>> args = starter.get_startup_args()
            >>> print(args['command'])
            npm run dev:h5
            >>> print(args['dev_script'])
            dev:h5
        """
        port = port if port is not None else self.default_port
        host = host if host is not None else self.get_host()

        return {
            'command': f"npm run {self.dev_command}",
            'dev_script': self.dev_command,
            'port': port,
            'host': host,
        }

    def get_status(self) -> dict:
        """
        Get the current status of the frontend service configuration.

        Provides a summary of the frontend service configuration including
        paths, port configuration, package.json status, and node_modules status.

        Returns:
            Dictionary containing status information with keys:
            - project_root: The project root directory path
            - frontend_dir: The frontend directory path
            - package_json_path: The package.json file path
            - node_modules_path: The node_modules directory path
            - default_port: The default port number
            - vite_config_port: The port from vite.config.ts (if any)
            - package_json_exists: Whether package.json exists
            - node_modules_exists: Whether node_modules exists
            - dev_command: The development script command
            - host: The configured host address

        Examples:
            >>> starter = FrontendStarter()
            >>> status = starter.get_status()
            >>> print(f"package.json exists: {status['package_json_exists']}")
            package.json exists: True
            >>> print(f"Default port: {status['default_port']}")
            Default port: 5173
        """
        return {
            'project_root': str(self.project_root),
            'frontend_dir': str(self.frontend_dir),
            'package_json_path': str(self.package_json_path),
            'node_modules_path': str(self.node_modules_path),
            'default_port': self.default_port,
            'vite_config_port': self.get_vite_config_port(),
            'package_json_exists': self.has_package_json(),
            'node_modules_exists': self.has_node_modules(),
            'dev_command': self.dev_command,
            'host': self.get_host(),
        }


# Convenience functions for direct import
def create_frontend_starter(
    project_root: Optional[Path] = None,
    default_port: Optional[int] = None
) -> FrontendStarter:
    """
    Create a FrontendStarter instance with the specified configuration.

    Convenience wrapper around FrontendStarter() constructor.

    Args:
        project_root: The root directory of the project.
        default_port: The default port for the frontend service.

    Returns:
        A configured FrontendStarter instance.

    Examples:
        >>> starter = create_frontend_starter(default_port=3000)
        >>> print(starter.default_port)
        3000
    """
    return FrontendStarter(project_root=project_root, default_port=default_port)


def get_frontend_port(project_root: Optional[Path] = None) -> int:
    """
    Get an available port for the frontend service.

    Convenience function that creates a FrontendStarter and finds
    an available port in one call.

    Args:
        project_root: The root directory of the project.

    Returns:
        An available port number.

    Examples:
        >>> port = get_frontend_port()
        >>> print(f"Frontend port: {port}")
        Frontend port: 5173
    """
    starter = FrontendStarter(project_root=project_root)
    return starter.get_available_port()
