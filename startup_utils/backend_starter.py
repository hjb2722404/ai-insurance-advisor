"""
Backend Service Starter Module

Provides backend-specific startup functionality including:
- Port detection and conflict resolution for the FastAPI backend
- .env file management with dynamic port updating
- Integration with uvicorn server startup
- Virtual environment detection and Python executable path resolution
- Dependency validation for backend requirements

This module handles the backend service startup logic, ensuring that
the service starts on an available port and that configuration is
properly set up.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from startup_utils.port_checker import find_available_port, is_port_in_use
from startup_utils.dependency_installer import DependencyInstaller


class BackendStarter:
    """
    Backend service starter class for managing FastAPI application startup.

    Handles port detection, .env file management, virtual environment
    detection, dependency validation, and provides the necessary
    configuration for starting the backend service with uvicorn.

    Attributes:
        default_port: The default port for the backend service (8000).
        project_root: The root directory of the project.
        backend_dir: The backend directory path.
        env_example_path: Path to the .env.example file.
        env_path: Path to the .env file.
        python_path: Path to the Python executable (sys.executable).
        venv_path: Path to the virtual environment directory, or None.

    Examples:
        >>> starter = BackendStarter()
        >>> starter.default_port
        8000
        >>> available_port = starter.get_available_port()
        >>> print(f"Backend will start on port {available_port}")
        Backend will start on port 8000
        >>> print(f"Python: {starter.python_path}")
        Python: /usr/bin/python
        >>> print(f"Venv: {starter.venv_path}")
        Venv: /path/to/project/venv
    """

    # Default configuration
    DEFAULT_PORT = 8000
    DEFAULT_HOST = '0.0.0.0'
    BACKEND_DIR = 'backend'
    ENV_EXAMPLE_FILE = '.env.example'
    ENV_FILE = '.env'
    VENV_NAMES = ['venv', '.venv', 'env', '.env', '.venv']

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
            >>> print(starter.python_path)
            /usr/bin/python
            >>> print(starter.venv_path)
            /path/to/project/venv
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

        # Set up Python executable path
        self.python_path = sys.executable

        # Detect virtual environment path
        self.venv_path = self._detect_venv_path()

    def _detect_venv_path(self) -> Optional[Path]:
        """
        Detect the virtual environment directory.

        Searches for common virtual environment directory names in the
        project root. Returns the path if found, None otherwise.

        Returns:
            Path to the virtual environment directory, or None if not found.

        Examples:
            >>> starter = BackendStarter()
            >>> starter.venv_path  # If venv exists
            PosixPath('/path/to/project/venv')
            >>> starter.venv_path  # If no venv exists
            None
        """
        for venv_name in self.VENV_NAMES:
            venv_path = self.project_root / venv_name
            if venv_path.exists() and venv_path.is_dir():
                # Check if it looks like a virtual environment
                # by verifying the presence of activation scripts
                if (venv_path / 'Scripts' / 'activate.bat').exists() or \
                   (venv_path / 'bin' / 'activate').exists():
                    return venv_path
        return None

    def is_in_venv(self) -> bool:
        """
        Check if the current Python is running in a virtual environment.

        Uses sys.prefix and sys.base_prefix to determine if we're in a venv.

        Returns:
            True if running in a virtual environment, False otherwise.

        Examples:
            >>> starter = BackendStarter()
            >>> starter.is_in_venv()
            True
        """
        return sys.prefix != sys.base_prefix

    def get_venv_python_path(self) -> Optional[Path]:
        """
        Get the path to the Python executable in the detected virtual environment.

        Returns the path to the Python executable inside the virtual environment,
        regardless of whether the current Python is running in that venv.

        Returns:
            Path to the venv Python executable, or None if no venv detected.

        Examples:
            >>> starter = BackendStarter()
            >>> starter.get_venv_python_path()
            PosixPath('/path/to/project/venv/bin/python')
        """
        if self.venv_path is None:
            return None

        # Determine the correct subdirectory based on platform
        if os.name == 'nt':  # Windows
            python_exe = self.venv_path / 'Scripts' / 'python.exe'
        else:  # Unix-like (Linux, macOS)
            python_exe = self.venv_path / 'bin' / 'python'

        return python_exe if python_exe.exists() else None

    def check_dependencies(self) -> Tuple[bool, list[str]]:
        """
        Check if all backend dependencies from requirements.txt are installed.

        Uses the DependencyInstaller to validate that all required packages
        are available in the current Python environment.

        Returns:
            A tuple of (all_satisfied: bool, missing_packages: list[str]).
            - all_satisfied: True if all dependencies are installed, False otherwise.
            - missing_packages: List of package names that are missing.

        Raises:
            FileNotFoundError: If requirements.txt doesn't exist.

        Examples:
            >>> starter = BackendStarter()
            >>> all_satisfied, missing = starter.check_dependencies()
            >>> if not all_satisfied:
            ...     print(f"Missing: {', '.join(missing)}")
            Missing: fastapi, uvicorn
        """
        requirements_file = self.backend_dir / 'requirements.txt'
        return DependencyInstaller.check_pip_dependencies(str(requirements_file))

    def install_dependencies(self) -> Tuple[bool, str]:
        """
        Install backend Python dependencies from requirements.txt.

        Uses the DependencyInstaller to install all required packages.
        If dependencies are already satisfied, returns success message.

        Returns:
            A tuple of (success: bool, message: str).
            - success: True if installation succeeded or deps already installed.
            - message: Success message or error details.

        Examples:
            >>> starter = BackendStarter()
            >>> success, message = starter.install_dependencies()
            >>> if success:
            ...     print(message)
            All backend dependencies are already installed
            >>> success, message = starter.install_dependencies()
            >>> if success:
            ...     print(message)
            Successfully installed 25 packages
        """
        installer = DependencyInstaller()
        return installer.install_backend_dependencies(str(self.backend_dir))

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
        paths, port configuration, environment file status, and virtual
        environment information.

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
            - python_path: The Python executable path
            - venv_path: The virtual environment directory path (or None)
            - in_venv: Whether currently running in a virtual environment
            - venv_python_path: The venv Python executable path (or None)

        Examples:
            >>> starter = BackendStarter()
            >>> status = starter.get_status()
            >>> print(f"Env file exists: {status['env_exists']}")
            Env file exists: True
            >>> print(f"Default port: {status['default_port']}")
            Default port: 8000
            >>> print(f"In venv: {status['in_venv']}")
            In venv: True
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
            'python_path': str(self.python_path),
            'venv_path': str(self.venv_path) if self.venv_path else None,
            'in_venv': self.is_in_venv(),
            'venv_python_path': str(self.get_venv_python_path()) if self.get_venv_python_path() else None,
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
