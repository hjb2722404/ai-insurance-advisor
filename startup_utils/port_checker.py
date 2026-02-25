"""
Port Checker Module

Provides cross-platform port detection and conflict resolution utilities
for service startup automation. Uses socket-based detection to determine
if a port is in use and can automatically find available ports by
incrementing from a starting port.
"""

import socket
from typing import Optional


def is_port_in_use(port: int, host: str = 'localhost', timeout: float = 0.1) -> bool:
    """
    Check if a port is currently in use on the specified host.

    Attempts to create a TCP connection to the specified host and port.
    If the connection succeeds, the port is considered to be in use.

    Args:
        port: The port number to check (1-65535).
        host: The host address to check. Defaults to 'localhost'.
        timeout: Connection timeout in seconds. Defaults to 0.1 for fast checks.

    Returns:
        True if the port is in use (connection succeeded), False otherwise.

    Raises:
        ValueError: If port is outside the valid range (1-65535).
        socket.gaierror: If the hostname cannot be resolved.

    Examples:
        >>> is_port_in_use(8000)
        True
        >>> is_port_in_use(9999)
        False
    """
    if not 1 <= port <= 65535:
        raise ValueError(
            f"Port must be between 1 and 65535, got {port}"
        )

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            # connect_ex returns 0 if connection succeeds
            return result == 0
    except socket.gaierror as e:
        # Re-raise host resolution errors with context
        raise socket.gaierror(
            f"Failed to resolve host '{host}': {str(e)}"
        ) from e
    except OSError as e:
        # Handle other socket-related errors (e.g., network issues)
        # Return False for network errors - port isn't "in use" if we can't reach it
        return False


def find_available_port(
    start_port: int,
    host: str = 'localhost',
    max_attempts: int = 100,
    timeout: float = 0.1
) -> Optional[int]:
    """
    Find an available port starting from the specified port number.

    Increments the port number until finding an available port or reaching
    the maximum number of attempts. Useful for finding alternative ports
    when default ports are occupied.

    Args:
        start_port: The starting port number to check (1-65535).
        host: The host address to check. Defaults to 'localhost'.
        max_attempts: Maximum number of ports to check. Defaults to 100.
        timeout: Connection timeout in seconds for each check. Defaults to 0.1.

    Returns:
        The first available port number, or None if no available port
        was found within max_attempts.

    Raises:
        ValueError: If start_port is outside the valid range (1-65535).

    Examples:
        >>> find_available_port(8000)
        8000
        >>> find_available_port(8000)  # When 8000 is in use
        8001
        >>> find_available_port(65500, max_attempts=100)  # Near upper limit
        None
    """
    if not 1 <= start_port <= 65535:
        raise ValueError(
            f"Start port must be between 1 and 65535, got {start_port}"
        )

    if max_attempts < 1:
        raise ValueError(
            f"Max attempts must be at least 1, got {max_attempts}"
        )

    port = start_port
    attempts = 0

    while attempts < max_attempts and port <= 65535:
        if not is_port_in_use(port, host, timeout):
            return port
        port += 1
        attempts += 1

    # No available port found
    return None


def get_port_info(port: int, host: str = 'localhost') -> dict:
    """
    Get detailed information about a port's status.

    Provides comprehensive information about whether a port is in use,
    and if so, attempts to provide additional context.

    Args:
        port: The port number to check (1-65535).
        host: The host address to check. Defaults to 'localhost'.

    Returns:
        Dictionary containing port information with keys:
        - port: The port number that was checked.
        - is_in_use: Boolean indicating if the port is currently in use.
        - host: The host that was checked.
        - error: Error message if the check failed, None otherwise.

    Raises:
        ValueError: If port is outside the valid range (1-65535).

    Examples:
        >>> get_port_info(8000)
        {
            'port': 8000,
            'is_in_use': True,
            'host': 'localhost',
            'error': None
        }
    """
    if not 1 <= port <= 65535:
        raise ValueError(
            f"Port must be between 1 and 65535, got {port}"
        )

    result = {
        'port': port,
        'is_in_use': False,
        'host': host,
        'error': None
    }

    try:
        result['is_in_use'] = is_port_in_use(port, host)
    except (socket.gaierror, OSError) as e:
        result['error'] = str(e)

    return result
