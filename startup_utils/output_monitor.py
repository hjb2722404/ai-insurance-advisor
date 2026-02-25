"""
Output Monitor Module

Provides pattern-based output monitoring utilities for detecting service
startup success and failure. Monitors command output in real-time and
identifies key indicators that signal whether a service has started
successfully or failed during initialization.
"""

import re
import threading
import time
from enum import Enum
from typing import Callable, Optional, List, Dict


class ServiceStatus(Enum):
    """
    Enumeration of possible service startup statuses.

    Attributes:
        PENDING: Service has not started yet.
        IN_PROGRESS: Service is currently starting up.
        SUCCESS: Service started successfully.
        FAILURE: Service failed to start.
        TIMEOUT: Service startup timed out.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class OutputMonitor:
    """
    Monitors command output to detect service startup success or failure.

    Provides pattern-based detection for common startup success and failure
    indicators from both backend (FastAPI/Uvicorn) and frontend (Vite)
    services. Maintains state tracking and can trigger callbacks when
    status changes are detected.

    Attributes:
        backend_success_patterns: Compiled regex patterns for backend success.
        backend_failure_patterns: Compiled regex patterns for backend failure.
        frontend_success_patterns: Compiled regex patterns for frontend success.
        frontend_failure_patterns: Compiled regex patterns for frontend failure.
        status: Current service status.
        matched_pattern: The pattern that caused the last status change.
    """

    # Backend success patterns (FastAPI/Uvicorn)
    BACKEND_SUCCESS_PATTERNS = [
        r'Application startup complete',
        r'Uvicorn running on http://[^\s]+',
        r'INFO:\s+Started server',
        r'INFO:\s+Application startup complete',
    ]

    # Backend failure patterns
    BACKEND_FAILURE_PATTERNS = [
        r'ERROR:\s+.*error',
        r'Error:\s+.*',
        r'Exception:\s+.*',
        r'Traceback \(most recent call last\):',
        r'Failed to start',
        r'Port \d+ is in use',
        r'Address already in use',
        r'Permission denied',
        r'No module named',
        r'ModuleNotFoundError',
        r'ImportError',
    ]

    # Frontend success patterns (Vite dev server)
    FRONTEND_SUCCESS_PATTERNS = [
        r'Local:\s+http://localhost:\d+',
        r'Network:\s+use --host to expose',
        r'ready in \d+ ms',
        r'VITE \d+\.\d+\.\d+\s+ready',
        r'➜\s+Local:',
    ]

    # Frontend failure patterns
    FRONTEND_FAILURE_PATTERNS = [
        r'ERROR:\s+.*',
        r'Error:\s+.*',
        r'Failed to compile',
        r'Failed to resolve',
        r'Cannot find module',
        r'sh: .*: not found',
        r'command not found',
        r'Port \d+ is in use',
        r'Address already in use',
        r'ENOSPC',
        r'EACCES',
    ]

    def __init__(self, service_type: str = 'backend') -> None:
        """
        Initialize the output monitor for a specific service type.

        Args:
            service_type: The type of service to monitor ('backend' or 'frontend').
                          Defaults to 'backend'.

        Raises:
            ValueError: If service_type is not 'backend' or 'frontend'.
        """
        if service_type not in ('backend', 'frontend'):
            raise ValueError(
                f"service_type must be 'backend' or 'frontend', got '{service_type}'"
            )

        self.service_type = service_type
        self.status = ServiceStatus.PENDING
        self.matched_pattern: Optional[str] = None
        self.output_lines: List[str] = []
        self._callbacks: List[Callable[[ServiceStatus, Optional[str]], None]] = []

        # Store raw pattern lists for verification access
        self.backend_success_patterns = self.BACKEND_SUCCESS_PATTERNS
        self.backend_failure_patterns = self.BACKEND_FAILURE_PATTERNS
        self.frontend_success_patterns = self.FRONTEND_SUCCESS_PATTERNS
        self.frontend_failure_patterns = self.FRONTEND_FAILURE_PATTERNS

        # Compile patterns based on service type
        if service_type == 'backend':
            self.success_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.BACKEND_SUCCESS_PATTERNS
            ]
            self.failure_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.BACKEND_FAILURE_PATTERNS
            ]
        else:  # frontend
            self.success_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.FRONTEND_SUCCESS_PATTERNS
            ]
            self.failure_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.FRONTEND_FAILURE_PATTERNS
            ]

    def add_callback(
        self,
        callback: Callable[[ServiceStatus, Optional[str]], None]
    ) -> None:
        """
        Add a callback function to be triggered on status changes.

        The callback will be called with (status, matched_pattern) arguments
        whenever the monitor's status changes.

        Args:
            callback: A callable that accepts (ServiceStatus, Optional[str]).

        Examples:
            >>> def on_status_change(status, pattern):
            ...     print(f"Status changed to: {status}")
            >>> monitor = OutputMonitor()
            >>> monitor.add_callback(on_status_change)
        """
        self._callbacks.append(callback)

    def process_line(self, line: str) -> ServiceStatus:
        """
        Process a single line of output and update status if patterns match.

        Checks the line against success and failure patterns. If a match is
        found, updates the internal status and triggers any registered callbacks.

        Args:
            line: A line of output from the service command.

        Returns:
            The current service status after processing this line.

        Examples:
            >>> monitor = OutputMonitor('backend')
            >>> monitor.process_line('INFO:     Application startup complete.')
            <ServiceStatus.SUCCESS: 'success'>
        """
        self.output_lines.append(line)
        line_stripped = line.strip()

        # Check for success patterns first
        for pattern in self.success_patterns:
            if pattern.search(line_stripped):
                self._update_status(ServiceStatus.SUCCESS, pattern.pattern)
                return self.status

        # Check for failure patterns
        for pattern in self.failure_patterns:
            if pattern.search(line_stripped):
                self._update_status(ServiceStatus.FAILURE, pattern.pattern)
                return self.status

        # Mark as in progress if we see any output
        if line_stripped and self.status == ServiceStatus.PENDING:
            self._update_status(ServiceStatus.IN_PROGRESS, None)

        return self.status

    def process_output(self, output: str) -> ServiceStatus:
        """
        Process multiple lines of output and update status if patterns match.

        Splits the output into lines and processes each one sequentially.
        Stops processing early if a success or failure status is detected.

        Args:
            output: Multi-line output from the service command.

        Returns:
            The final service status after processing all lines.

        Examples:
            >>> monitor = OutputMonitor('frontend')
            >>> output = "VITE v4.4.9 ready in 234 ms\\n➜  Local:   http://localhost:5173/"
            >>> monitor.process_output(output)
            <ServiceStatus.SUCCESS: 'success'>
        """
        lines = output.split('\n')
        for line in lines:
            current_status = self.process_line(line)
            # Stop processing if we've reached a terminal state
            if current_status in (ServiceStatus.SUCCESS, ServiceStatus.FAILURE):
                break

        return self.status

    def wait_for_completion(
        self,
        timeout: float = 30.0,
        check_interval: float = 0.1
    ) -> ServiceStatus:
        """
        Wait for the service to reach a terminal state (success or failure).

        Blocks until the status changes to SUCCESS or FAILURE, or until the
        timeout is reached.

        Args:
            timeout: Maximum time to wait in seconds. Defaults to 30.0.
            check_interval: Time between status checks in seconds. Defaults to 0.1.

        Returns:
            The final service status (SUCCESS, FAILURE, or TIMEOUT).

        Examples:
            >>> monitor = OutputMonitor('backend')
            >>> # Start service in background...
            >>> status = monitor.wait_for_completion(timeout=10)
            >>> if status == ServiceStatus.SUCCESS:
            ...     print("Service started successfully")
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.status in (ServiceStatus.SUCCESS, ServiceStatus.FAILURE):
                return self.status
            time.sleep(check_interval)

        self._update_status(ServiceStatus.TIMEOUT, None)
        return self.status

    def get_status_info(self) -> Dict:
        """
        Get comprehensive status information about the monitored service.

        Returns:
            Dictionary containing:
            - service_type: The type of service being monitored.
            - status: Current ServiceStatus.
            - matched_pattern: The pattern that caused the last status change.
            - output_lines: List of all output lines processed so far.
            - line_count: Number of output lines processed.

        Examples:
            >>> monitor = OutputMonitor('backend')
            >>> monitor.process_line('INFO: Started server')
            >>> info = monitor.get_status_info()
            >>> info['status']
            <ServiceStatus.IN_PROGRESS: 'in_progress'>
        """
        return {
            'service_type': self.service_type,
            'status': self.status.value,
            'matched_pattern': self.matched_pattern,
            'output_lines': self.output_lines,
            'line_count': len(self.output_lines),
        }

    def reset(self) -> None:
        """
        Reset the monitor to its initial state.

        Clears status, matched patterns, and output history. Callbacks
        are preserved.

        Examples:
            >>> monitor = OutputMonitor('backend')
            >>> monitor.process_line('Some output')
            >>> monitor.reset()
            >>> monitor.status
            <ServiceStatus.PENDING: 'pending'>
        """
        self.status = ServiceStatus.PENDING
        self.matched_pattern = None
        self.output_lines = []

    def _update_status(
        self,
        new_status: ServiceStatus,
        pattern: Optional[str]
    ) -> None:
        """
        Internal method to update status and trigger callbacks.

        Args:
            new_status: The new service status.
            pattern: The regex pattern that caused the status change.
        """
        old_status = self.status
        self.status = new_status
        self.matched_pattern = pattern

        # Only trigger callbacks on status changes
        if old_status != new_status:
            for callback in self._callbacks:
                try:
                    callback(new_status, pattern)
                except Exception:
                    # Don't let callback errors break monitoring
                    pass


def create_monitor(service_type: str = 'backend') -> OutputMonitor:
    """
    Create an output monitor for the specified service type.

    Convenience factory function for creating OutputMonitor instances.

    Args:
        service_type: The type of service to monitor ('backend' or 'frontend').

    Returns:
        A configured OutputMonitor instance.

    Examples:
        >>> monitor = create_monitor('backend')
        >>> isinstance(monitor, OutputMonitor)
        True
    """
    return OutputMonitor(service_type)


# Convenience functions for quick checks
def detect_backend_success(output: str) -> bool:
    """
    Quick check if output indicates backend startup success.

    Scans output for backend success patterns. Does not maintain state.

    Args:
        output: The command output to check.

    Returns:
        True if any backend success pattern is found, False otherwise.

    Examples:
        >>> detect_backend_success('Application startup complete')
        True
    """
    monitor = OutputMonitor('backend')
    monitor.process_output(output)
    return monitor.status == ServiceStatus.SUCCESS


def detect_frontend_success(output: str) -> bool:
    """
    Quick check if output indicates frontend startup success.

    Scans output for frontend success patterns. Does not maintain state.

    Args:
        output: The command output to check.

    Returns:
        True if any frontend success pattern is found, False otherwise.

    Examples:
        >>> detect_frontend_success('Local: http://localhost:5173/')
        True
    """
    monitor = OutputMonitor('frontend')
    monitor.process_output(output)
    return monitor.status == ServiceStatus.SUCCESS


def detect_failure(output: str, service_type: str = 'backend') -> bool:
    """
    Quick check if output indicates service startup failure.

    Scans output for failure patterns. Does not maintain state.

    Args:
        output: The command output to check.
        service_type: The type of service ('backend' or 'frontend').

    Returns:
        True if any failure pattern is found, False otherwise.

    Examples:
        >>> detect_failure('Error: Port 8000 is in use', 'backend')
        True
    """
    monitor = OutputMonitor(service_type)
    monitor.process_output(output)
    return monitor.status == ServiceStatus.FAILURE
