"""
Command Validator

Provides cross-platform command existence checking utilities
for service startup validation.
"""

import shutil
import subprocess
from typing import Optional, Tuple


class CommandValidator:
    """
    Utility class for validating command availability on the system.

    Provides methods to check if commands exist and are executable
    across different operating systems (Windows, Linux, macOS).
    """

    def __init__(self) -> None:
        """
        Initialize the command validator.

        No setup required as all methods are static utilities.
        """
        pass

    @staticmethod
    def command_exists(command: str) -> bool:
        """
        Check if a command exists on the system.

        Uses shutil.which() for cross-platform compatibility.
        This method checks if the command is available in the system's PATH.

        Args:
            command: The command name to check (e.g., 'python', 'npm', 'node').

        Returns:
            True if the command exists and is executable, False otherwise.

        Examples:
            >>> CommandValidator.command_exists('python')
            True
            >>> CommandValidator.command_exists('npm')
            True
            >>> CommandValidator.command_exists('nonexistent')
            False
        """
        return shutil.which(command) is not None

    @staticmethod
    def get_command_path(command: str) -> Optional[str]:
        """
        Get the full path to a command if it exists.

        Uses shutil.which() to locate the command in the system's PATH.

        Args:
            command: The command name to locate (e.g., 'python', 'npm').

        Returns:
            The full path to the command if found, None otherwise.

        Examples:
            >>> CommandValidator.get_command_path('python')
            '/usr/bin/python'
            >>> CommandValidator.get_command_path('nonexistent')
            None
        """
        return shutil.which(command)

    @staticmethod
    def check_version(command: str, version_arg: str = '--version') -> Tuple[bool, Optional[str]]:
        """
        Check if a command exists and get its version information.

        Attempts to run the command with a version argument and capture
        the output. Handles both successful execution and errors gracefully.

        Args:
            command: The command name to check (e.g., 'python', 'node').
            version_arg: The argument to request version info. Default is '--version'.
                        Some commands use '-v' or '-V' instead.

        Returns:
            A tuple of (success: bool, version_output: Optional[str]).
            - success: True if the command executed successfully, False otherwise.
            - version_output: The version string if successful, None or error message if failed.

        Examples:
            >>> CommandValidator.check_version('python')
            (True, 'Python 3.11.5')
            >>> CommandValidator.check_version('node', '--version')
            (True, 'v20.5.0')
            >>> CommandValidator.check_version('nonexistent')
            (False, None)
        """
        command_path = shutil.which(command)
        if command_path is None:
            return False, None

        try:
            result = subprocess.run(
                [command, version_arg],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )

            if result.returncode == 0:
                version_info = result.stdout.strip() or result.stderr.strip()
                return True, version_info
            else:
                return False, None

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def validate_commands(commands: list[str]) -> dict[str, dict]:
        """
        Validate multiple commands and return their status.

        Checks each command for existence and optionally retrieves version info.
        Returns a comprehensive status report for all commands.

        Args:
            commands: List of command names to validate (e.g., ['python', 'npm', 'node']).

        Returns:
            Dictionary mapping command names to their status with keys:
            - exists: Boolean indicating if the command is available
            - path: Full path to the command if found, None otherwise
            - version: Version string if retrievable, None otherwise
            - error: Error message if validation failed, None otherwise

        Examples:
            >>> CommandValidator.validate_commands(['python', 'npm'])
            {
                'python': {'exists': True, 'path': '/usr/bin/python', 'version': '3.11.5', 'error': None},
                'npm': {'exists': True, 'path': '/usr/bin/npm', 'version': '10.0.0', 'error': None}
            }
        """
        results = {}

        for command in commands:
            result = {
                'exists': False,
                'path': None,
                'version': None,
                'error': None
            }

            try:
                # Check if command exists
                command_path = shutil.which(command)
                if command_path is None:
                    result['error'] = f"Command '{command}' not found in PATH"
                    results[command] = result
                    continue

                result['exists'] = True
                result['path'] = command_path

                # Try to get version
                success, version_info = CommandValidator.check_version(command)
                if success and version_info:
                    result['version'] = version_info

            except Exception as e:
                result['error'] = str(e)

            results[command] = result

        return results


# Convenience functions for direct import
def command_exists(command: str) -> bool:
    """
    Check if a command exists on the system.

    Convenience wrapper around CommandValidator.command_exists().

    Args:
        command: The command name to check.

    Returns:
        True if the command exists, False otherwise.
    """
    return CommandValidator.command_exists(command)


def get_command_path(command: str) -> Optional[str]:
    """
    Get the full path to a command if it exists.

    Convenience wrapper around CommandValidator.get_command_path().

    Args:
        command: The command name to locate.

    Returns:
        The full path to the command if found, None otherwise.
    """
    return CommandValidator.get_command_path(command)
