"""
Dependency Installer Module

Provides automatic dependency installation utilities for both
Python (pip) and Node.js (npm) environments. Handles virtual
environment detection, package installation, and dependency validation.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


class DependencyInstaller:
    """
    Utility class for installing and managing project dependencies.

    Supports both Python pip installations for backend services
    and npm installations for frontend services. Handles virtual
    environments and provides detailed installation feedback.
    """

    def __init__(self) -> None:
        """
        Initialize the dependency installer.

        Sets up default paths and configuration for dependency
        installation operations.
        """
        self.project_root = Path.cwd()

    @staticmethod
    def check_pip_dependencies(requirements_path: str) -> Tuple[bool, list[str]]:
        """
        Check if all pip dependencies from requirements.txt are installed.

        Parses the requirements file and checks if each package is
        currently available in the Python environment.

        Args:
            requirements_path: Path to the requirements.txt file.

        Returns:
            A tuple of (all_satisfied: bool, missing_packages: list[str]).
            - all_satisfied: True if all dependencies are installed, False otherwise.
            - missing_packages: List of package names that are missing.

        Raises:
            FileNotFoundError: If the requirements file doesn't exist.
            ValueError: If the requirements path is invalid.

        Examples:
            >>> DependencyInstaller.check_pip_dependencies('backend/requirements.txt')
            (True, [])
            >>> DependencyInstaller.check_pip_dependencies('backend/requirements.txt')
            (False, ['fastapi', 'uvicorn'])
        """
        requirements_file = Path(requirements_path)
        if not requirements_file.exists():
            raise FileNotFoundError(
                f"Requirements file not found: {requirements_path}"
            )

        missing_packages = []

        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines, comments, and environment markers
                    if not line or line.startswith('#') or line.startswith('-'):
                        continue

                    # Extract package name (before any version specifier)
                    # Handles: package, package==1.0, package>=1.0, package[extras]
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('[')[0].strip()

                    # Try to import the package to check if it's installed
                    # Normalize package name: replace hyphens with underscores for Python imports
                    import_name = package_name.replace('-', '_').lower()

                    try:
                        # Special handling for packages with different import names
                        if package_name == 'pymupdf':
                            import_name = 'fitz'
                        elif package_name == 'pydantic-settings':
                            import_name = 'pydantic_settings'

                        __import__(import_name)
                    except ImportError:
                        missing_packages.append(package_name)

        except FileNotFoundError:
            raise
        except Exception as e:
            raise ValueError(
                f"Failed to parse requirements file: {str(e)}"
            ) from e

        all_satisfied = len(missing_packages) == 0
        return all_satisfied, missing_packages

    @staticmethod
    def install_pip_dependencies(
        requirements_path: str,
        python_path: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Install Python dependencies from a requirements.txt file.

        Runs pip install with the specified requirements file.
        Uses the provided Python executable path or defaults to sys.executable.

        Args:
            requirements_path: Path to the requirements.txt file.
            python_path: Optional path to Python executable. If None, uses sys.executable.

        Returns:
            A tuple of (success: bool, message: str).
            - success: True if installation succeeded, False otherwise.
            - message: Success message or error details.

        Raises:
            FileNotFoundError: If the requirements file doesn't exist.

        Examples:
            >>> DependencyInstaller.install_pip_dependencies('backend/requirements.txt')
            (True, 'Successfully installed 25 packages')
            >>> DependencyInstaller.install_pip_dependencies('backend/requirements.txt')
            (False, 'Failed to install: error details...')
        """
        requirements_file = Path(requirements_path)
        if not requirements_file.exists():
            raise FileNotFoundError(
                f"Requirements file not found: {requirements_path}"
            )

        python_exe = python_path or sys.executable
        pip_command = [python_exe, '-m', 'pip', 'install', '-r', str(requirements_file)]

        try:
            result = subprocess.run(
                pip_command,
                capture_output=True,
                text=True,
                check=False,
                # Add a reasonable timeout for installation
                timeout=300  # 5 minutes
            )

            if result.returncode == 0:
                # Extract summary from output
                output = result.stdout + result.stderr
                # Try to find the "Successfully installed" line
                for line in output.split('\n'):
                    if 'Successfully installed' in line:
                        return True, line.strip()

                return True, 'Dependencies installed successfully'
            else:
                error_msg = result.stderr or result.stdout
                # Extract last few lines of error for context
                error_lines = error_msg.strip().split('\n')[-5:]
                return False, 'Installation failed: ' + '\n'.join(error_lines)

        except subprocess.TimeoutExpired:
            return False, 'Installation timed out after 5 minutes'
        except Exception as e:
            return False, f'Installation failed: {str(e)}'

    @staticmethod
    def check_npm_dependencies(package_json_path: str) -> Tuple[bool, bool]:
        """
        Check if npm dependencies are installed for a project.

        Checks for the existence of node_modules directory and
        validates that it's not empty.

        Args:
            package_json_path: Path to the package.json file or its directory.

        Returns:
            A tuple of (has_node_modules: bool, is_complete: bool).
            - has_node_modules: True if node_modules directory exists.
            - is_complete: True if node_modules appears to be complete (not empty).

        Raises:
            FileNotFoundError: If the package.json file doesn't exist.
            ValueError: If the path is invalid.

        Examples:
            >>> DependencyInstaller.check_npm_dependencies('frontend')
            (True, True)
            >>> DependencyInstaller.check_npm_dependencies('frontend')
            (False, False)
        """
        path = Path(package_json_path)

        # If path points to package.json, get its parent directory
        if path.is_file() and path.name == 'package.json':
            frontend_dir = path.parent
        elif path.is_dir():
            # Check if package.json exists in this directory
            if not (path / 'package.json').exists():
                raise FileNotFoundError(
                    f"package.json not found in directory: {package_json_path}"
                )
            frontend_dir = path
        else:
            raise ValueError(
                f"Invalid path, must be a directory or package.json file: {package_json_path}"
            )

        node_modules = frontend_dir / 'node_modules'

        has_node_modules = node_modules.exists() and node_modules.is_dir()

        # Check if node_modules is not empty (has at least some subdirectories)
        is_complete = False
        if has_node_modules:
            try:
                # Count subdirectories - a complete install has many packages
                subdirs = [d for d in node_modules.iterdir() if d.is_dir() and not d.name.startswith('.')]
                is_complete = len(subdirs) > 10  # Arbitrary threshold for "complete"
            except Exception:
                is_complete = False

        return has_node_modules, is_complete

    @staticmethod
    def install_npm_dependencies(
        package_json_path: str,
        npm_path: str = 'npm'
    ) -> Tuple[bool, str]:
        """
        Install npm dependencies for a project using npm install.

        Runs npm install in the directory containing package.json.

        Args:
            package_json_path: Path to the package.json file or its directory.
            npm_path: Path or command name for npm. Defaults to 'npm'.

        Returns:
            A tuple of (success: bool, message: str).
            - success: True if installation succeeded, False otherwise.
            - message: Success message with package count or error details.

        Raises:
            FileNotFoundError: If the package.json file doesn't exist.
            ValueError: If the path is invalid.

        Examples:
            >>> DependencyInstaller.install_npm_dependencies('frontend')
            (True, 'Successfully installed 156 packages')
            >>> DependencyInstaller.install_npm_dependencies('frontend')
            (False, 'Installation failed: error details...')
        """
        path = Path(package_json_path)

        # If path points to package.json, get its parent directory
        if path.is_file() and path.name == 'package.json':
            frontend_dir = path.parent
        elif path.is_dir():
            # Check if package.json exists in this directory
            if not (path / 'package.json').exists():
                raise FileNotFoundError(
                    f"package.json not found in directory: {package_json_path}"
                )
            frontend_dir = path
        else:
            raise ValueError(
                f"Invalid path, must be a directory or package.json file: {package_json_path}"
            )

        npm_command = [npm_path, 'install']

        try:
            result = subprocess.run(
                npm_command,
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                check=False,
                timeout=300  # 5 minutes
            )

            if result.returncode == 0:
                # Try to extract package count from output
                output = result.stdout + result.stderr

                # Look for patterns like "added 156 packages"
                import re
                match = re.search(r'added\s+(\d+)\s+package', output)
                if match:
                    count = match.group(1)
                    return True, f"Successfully installed {count} packages"

                # Look for "up to date" message
                if 'up to date' in output.lower():
                    return True, "Dependencies are already up to date"

                return True, 'Dependencies installed successfully'
            else:
                error_msg = result.stderr or result.stdout
                # Extract last few lines of error for context
                error_lines = error_msg.strip().split('\n')[-5:]
                return False, 'Installation failed: ' + '\n'.join(error_lines)

        except subprocess.TimeoutExpired:
            return False, 'Installation timed out after 5 minutes'
        except FileNotFoundError:
            return False, f"npm command not found. Please ensure Node.js is installed."
        except Exception as e:
            return False, f'Installation failed: {str(e)}'

    def install_backend_dependencies(
        self,
        backend_dir: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Install backend Python dependencies.

        Convenience method that checks requirements.txt and installs
        missing dependencies for the backend service.

        Args:
            backend_dir: Path to backend directory. If None, uses 'backend' from project root.

        Returns:
            A tuple of (success: bool, message: str).

        Examples:
            >>> installer = DependencyInstaller()
            >>> installer.install_backend_dependencies()
            (True, 'All backend dependencies are already installed')
            >>> installer.install_backend_dependencies()
            (True, 'Successfully installed 25 packages')
        """
        if backend_dir is None:
            backend_dir = self.project_root / 'backend'
        else:
            backend_dir = Path(backend_dir)

        requirements_file = backend_dir / 'requirements.txt'

        if not requirements_file.exists():
            return False, f"Requirements file not found: {requirements_file}"

        # Check if dependencies are already installed
        all_satisfied, missing = self.check_pip_dependencies(str(requirements_file))

        if all_satisfied:
            return True, 'All backend dependencies are already installed'

        # Install missing dependencies
        success, message = self.install_pip_dependencies(str(requirements_file))

        if success:
            return True, message
        else:
            return False, f"Failed to install backend dependencies: {message}"

    def install_frontend_dependencies(
        self,
        frontend_dir: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Install frontend npm dependencies.

        Convenience method that checks node_modules and installs
        dependencies for the frontend service if needed.

        Args:
            frontend_dir: Path to frontend directory. If None, uses 'frontend' from project root.

        Returns:
            A tuple of (success: bool, message: str).

        Examples:
            >>> installer = DependencyInstaller()
            >>> installer.install_frontend_dependencies()
            (True, 'All frontend dependencies are already installed')
            >>> installer.install_frontend_dependencies()
            (True, 'Successfully installed 156 packages')
        """
        if frontend_dir is None:
            frontend_dir = self.project_root / 'frontend'
        else:
            frontend_dir = Path(frontend_dir)

        package_json = frontend_dir / 'package.json'

        if not package_json.exists():
            return False, f"package.json not found: {package_json}"

        # Check if dependencies are already installed
        has_modules, is_complete = self.check_npm_dependencies(str(package_json))

        if has_modules and is_complete:
            return True, 'All frontend dependencies are already installed'

        # Install dependencies
        success, message = self.install_npm_dependencies(str(package_json))

        if success:
            return True, message
        else:
            return False, f"Failed to install frontend dependencies: {message}"


# Convenience functions for direct import
def check_pip_dependencies(requirements_path: str) -> Tuple[bool, list[str]]:
    """
    Check if all pip dependencies from requirements.txt are installed.

    Convenience wrapper around DependencyInstaller.check_pip_dependencies().

    Args:
        requirements_path: Path to the requirements.txt file.

    Returns:
        A tuple of (all_satisfied: bool, missing_packages: list[str]).
    """
    return DependencyInstaller.check_pip_dependencies(requirements_path)


def install_pip_dependencies(
    requirements_path: str,
    python_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Install Python dependencies from a requirements.txt file.

    Convenience wrapper around DependencyInstaller.install_pip_dependencies().

    Args:
        requirements_path: Path to the requirements.txt file.
        python_path: Optional path to Python executable.

    Returns:
        A tuple of (success: bool, message: str).
    """
    return DependencyInstaller.install_pip_dependencies(requirements_path, python_path)


def check_npm_dependencies(package_json_path: str) -> Tuple[bool, bool]:
    """
    Check if npm dependencies are installed for a project.

    Convenience wrapper around DependencyInstaller.check_npm_dependencies().

    Args:
        package_json_path: Path to the package.json file or its directory.

    Returns:
        A tuple of (has_node_modules: bool, is_complete: bool).
    """
    return DependencyInstaller.check_npm_dependencies(package_json_path)


def install_npm_dependencies(
    package_json_path: str,
    npm_path: str = 'npm'
) -> Tuple[bool, str]:
    """
    Install npm dependencies for a project.

    Convenience wrapper around DependencyInstaller.install_npm_dependencies().

    Args:
        package_json_path: Path to the package.json file or its directory.
        npm_path: Path or command name for npm.

    Returns:
        A tuple of (success: bool, message: str).
    """
    return DependencyInstaller.install_npm_dependencies(package_json_path, npm_path)
