"""
Backend Service Starter Module

Provides backend-specific startup functionality including:
- Port detection and conflict resolution for the FastAPI backend
- .env file management with dynamic port updating
- Integration with uvicorn server startup

This module handles the backend service startup logic, ensuring that
the service starts on an available port and that configuration is
properly set up.
"""

import os
from pathlib import Path
from typing import Optional

from startup_utils.port_checker import find_available_port, is_port_in_use


class BackendStarter:
    """
    Backend service starter class for managing FastAPI application startup.

    Handles port detection, .env file management, and provides the
    necessary configuration for starting the backend service with uvicorn.

    Attributes:
        default_port: The default port for the backend service (8000).
        project_root: The root directory of the project.
        backend_dir: The backend directory path.
        env_example_path: Path to the .env.example file.
        env_path: Path to the .env file.

    Examples:
        >>> starter = BackendStarter()
        >>> starter.default_port
        8000
        >>> available_port = starter.get_available_port()
        >>> print(f"Backend will start on port {available_port}")
        Backend will start on port 8000
    """

    # Default configuration
    DEFAULT_PORT = 8000
    DEFAULT_HOST = '0.0.0.0'
    BACKEND_DIR = 'backend'
    ENV_EXAMPLE_FILE = '.env.example'
    ENV_FILE = '.env'

    def __init__(
        self,
        project_root: Optional[Path] = None,
        default_port: Optional[int] = None
    ) -> None:
        """
        Initialize the backend service starter.

        Sets up paths and configuration for backend service startup.
        If project_root is not provided, it will be detected automatically
        from the current working directory.

        Args:
            project_root: The root directory of the project.
                        If None, uses the current working directory.
            default_port: The default port to use for the backend.
                         If None, uses DEFAULT_PORT (8000).

        Examples:
            >>> starter = BackendStarter()
            >>> print(starter.default_port)
            8000
            >>> starter = BackendStarter(default_port=9000)
            >>> print(starter.default_port)
            9000
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
        self.backend_dir = self.project_root / self.BACKEND_DIR
        self.env_example_path = self.backend_dir / self.ENV_EXAMPLE_FILE
        self.env_path = self.backend_dir / self.ENV_FILE

    def get_available_port(
        self,
        start_port: Optional[int] = None,
        host: str = 'localhost'
    ) -> int:
        """
        Find an available port for the backend service.

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
            >>> starter = BackendStarter()
            >>> port = starter.get_available_port()
            >>> print(f"Available port: {port}")
            Available port: 8000
            >>> # If port 8000 is in use
            >>> port = starter.get_available_port()
            >>> print(f"Available port: {port}")
            Available port: 8001
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
        Check if a specific port is available for the backend service.

        Args:
            port: The port number to check.
            host: The host address to check. Defaults to 'localhost'.

        Returns:
            True if the port is available, False if it's in use.

        Examples:
            >>> starter = BackendStarter()
            >>> starter.is_port_available(8000)
            False
            >>> starter.is_port_available(8001)
            True
        """
        return not is_port_in_use(port, host=host)

    def get_env_port(self) -> Optional[int]:
        """
        Get the port configured in the .env file.

        Reads the API_PORT value from the backend's .env file if it exists.

        Returns:
            The port number from the .env file, or None if not configured.

        Examples:
            >>> starter = BackendStarter()
            >>> port = starter.get_env_port()
            >>> print(f"Configured port: {port}")
            Configured port: 8000
        """
        if not self.env_path.exists():
            return None

        try:
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('API_PORT='):
                        port_str = line.split('=', 1)[1].strip()
                        try:
                            return int(port_str)
                        except ValueError:
                            return None
        except (OSError, IOError) as e:
            # Log error but don't raise - this is a non-critical operation
            pass

        return None

    def get_host(self) -> str:
        """
        Get the host address for the backend service.

        Returns the configured host from the .env file if available,
        otherwise returns the default host.

        Returns:
            The host address (e.g., '0.0.0.0', 'localhost').

        Examples:
            >>> starter = BackendStarter()
            >>> host = starter.get_host()
            >>> print(f"Host: {host}")
            Host: 0.0.0.0
        """
        # Check .env file for API_HOST configuration
        if self.env_path.exists():
            try:
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('API_HOST='):
                            host = line.split('=', 1)[1].strip()
                            if host:
                                return host
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
        Get the uvicorn startup command for the backend service.

        Constructs the command to start the FastAPI backend with uvicorn,
        using the specified or detected port and host.

        Args:
            port: The port to use. If None, uses the default port.
            host: The host to use. If None, uses the default host.

        Returns:
            The uvicorn startup command string.

        Examples:
            >>> starter = BackendStarter()
            >>> cmd = starter.get_startup_command(port=8000)
            >>> print(cmd)
            uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
        """
        port = port if port is not None else self.default_port
        host = host if host is not None else self.get_host()

        return (
            f"uvicorn backend.app.main:app "
            f"--host {host} "
            f"--port {port} "
            f"--reload"
        )

    def get_startup_args(
        self,
        port: Optional[int] = None,
        host: Optional[str] = None
    ) -> dict:
        """
        Get the startup arguments for the backend service.

        Returns a dictionary with all the necessary configuration
        for starting the backend service programmatically.

        Args:
            port: The port to use. If None, uses the default port.
            host: The host to use. If None, uses the default host.

        Returns:
            Dictionary containing startup configuration with keys:
            - module: The Python module to run (backend.app.main:app)
            - host: The host address
            - port: The port number
            - reload: Whether to enable auto-reload (True)

        Examples:
            >>> starter = BackendStarter()
            >>> args = starter.get_startup_args(port=8000)
            >>> print(args['port'])
            8000
            >>> print(args['host'])
            0.0.0.0
        """
        port = port if port is not None else self.default_port
        host = host if host is not None else self.get_host()

        return {
            'module': 'backend.app.main:app',
            'host': host,
            'port': port,
            'reload': True,
        }

    def has_env_file(self) -> bool:
        """
        Check if the backend .env file exists.

        Returns:
            True if the .env file exists, False otherwise.

        Examples:
            >>> starter = BackendStarter()
            >>> starter.has_env_file()
            True
        """
        return self.env_path.exists()

    def has_env_example(self) -> bool:
        """
        Check if the backend .env.example file exists.

        Returns:
            True if the .env.example file exists, False otherwise.

        Examples:
            >>> starter = BackendStarter()
            >>> starter.has_env_example()
            True
        """
        return self.env_example_path.exists()

    def get_status(self) -> dict:
        """
        Get the current status of the backend service configuration.

        Provides a summary of the backend service configuration including
        paths, port configuration, and environment file status.

        Returns:
            Dictionary containing status information with keys:
            - project_root: The project root directory path
            - backend_dir: The backend directory path
            - env_path: The .env file path
            - env_example_path: The .env.example file path
            - default_port: The default port number
            - env_port: The port configured in .env (if any)
            - env_exists: Whether .env file exists
            - env_example_exists: Whether .env.example exists
            - host: The configured host address

        Examples:
            >>> starter = BackendStarter()
            >>> status = starter.get_status()
            >>> print(f"Env file exists: {status['env_exists']}")
            Env file exists: True
            >>> print(f"Default port: {status['default_port']}")
            Default port: 8000
        """
        return {
            'project_root': str(self.project_root),
            'backend_dir': str(self.backend_dir),
            'env_path': str(self.env_path),
            'env_example_path': str(self.env_example_path),
            'default_port': self.default_port,
            'env_port': self.get_env_port(),
            'env_exists': self.has_env_file(),
            'env_example_exists': self.has_env_example(),
            'host': self.get_host(),
        }


# Convenience functions for direct import
def create_backend_starter(
    project_root: Optional[Path] = None,
    default_port: Optional[int] = None
) -> BackendStarter:
    """
    Create a BackendStarter instance with the specified configuration.

    Convenience wrapper around BackendStarter() constructor.

    Args:
        project_root: The root directory of the project.
        default_port: The default port for the backend service.

    Returns:
        A configured BackendStarter instance.

    Examples:
        >>> starter = create_backend_starter(default_port=9000)
        >>> print(starter.default_port)
        9000
    """
    return BackendStarter(project_root=project_root, default_port=default_port)


def get_backend_port(project_root: Optional[Path] = None) -> int:
    """
    Get an available port for the backend service.

    Convenience function that creates a BackendStarter and finds
    an available port in one call.

    Args:
        project_root: The root directory of the project.

    Returns:
        An available port number.

    Examples:
        >>> port = get_backend_port()
        >>> print(f"Backend port: {port}")
        Backend port: 8000
    """
    starter = BackendStarter(project_root=project_root)
    return starter.get_available_port()
