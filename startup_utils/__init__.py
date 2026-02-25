"""
Startup Utilities Package

Provides cross-platform utilities for service startup automation including:
- Port detection and conflict resolution
- Command validation and dependency checking
- Output monitoring for service startup verification
- Automatic dependency installation

This package is designed to support the main startup script in managing
frontend and backend services with automatic port conflict detection
and resolution.
"""

from startup_utils.port_checker import is_port_in_use, find_available_port
from startup_utils.output_monitor import (
    OutputMonitor,
    ServiceStatus,
    create_monitor,
    detect_backend_success,
    detect_frontend_success,
    detect_failure,
)

__all__ = [
    "is_port_in_use",
    "find_available_port",
    "OutputMonitor",
    "ServiceStatus",
    "create_monitor",
    "detect_backend_success",
    "detect_frontend_success",
    "detect_failure",
]
