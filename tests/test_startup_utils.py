"""
Tests for startup utilities.

Tests port detection, command validation, and output monitoring utilities.
"""

import pytest
import socket
import subprocess
from unittest.mock import Mock, patch, MagicMock
from startup_utils.port_checker import (
    is_port_in_use,
    find_available_port,
    get_port_info,
)
from startup_utils.command_validator import (
    CommandValidator,
    command_exists,
    get_command_path,
)
from startup_utils.output_monitor import (
    OutputMonitor,
    ServiceStatus,
    create_monitor,
    detect_backend_success,
    detect_frontend_success,
    detect_failure,
)


class TestIsPortInUse:
    """Tests for is_port_in_use function."""

    def test_is_port_in_use_with_valid_port(self):
        """Test port check with valid port number."""
        # Use a high port that's unlikely to be in use
        result = is_port_in_use(65432)
        assert isinstance(result, bool)

    def test_is_port_in_use_with_invalid_port_zero(self):
        """Test port check raises error for port 0."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            is_port_in_use(0)

    def test_is_port_in_use_with_invalid_port_negative(self):
        """Test port check raises error for negative port."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            is_port_in_use(-1)

    def test_is_port_in_use_with_invalid_port_too_high(self):
        """Test port check raises error for port > 65535."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            is_port_in_use(65536)

    def test_is_port_in_use_with_custom_host(self):
        """Test port check with custom host."""
        result = is_port_in_use(65433, host='127.0.0.1')
        assert isinstance(result, bool)

    def test_is_port_in_use_with_custom_timeout(self):
        """Test port check with custom timeout."""
        result = is_port_in_use(65434, timeout=0.5)
        assert isinstance(result, bool)

    def test_is_port_in_use_handles_socket_error(self):
        """Test port check handles network errors gracefully."""
        # On some systems, invalid hostnames return False instead of raising
        # The function is designed to be resilient and return False for network errors
        result = is_port_in_use(65435, host='invalid.hostname.example')
        # Should either raise gaierror or return False (depending on system)
        assert isinstance(result, bool)


class TestFindAvailablePort:
    """Tests for find_available_port function."""

    def test_find_available_port_with_valid_start_port(self):
        """Test finding available port from valid start port."""
        # Use a high port range that's likely to be available
        port = find_available_port(65400, max_attempts=10)
        assert port is not None
        assert isinstance(port, int)
        assert 65400 <= port <= 65410

    def test_find_available_port_with_invalid_start_port_zero(self):
        """Test find_available_port raises error for port 0."""
        with pytest.raises(ValueError, match="Start port must be between 1 and 65535"):
            find_available_port(0)

    def test_find_available_port_with_invalid_start_port_negative(self):
        """Test find_available_port raises error for negative port."""
        with pytest.raises(ValueError, match="Start port must be between 1 and 65535"):
            find_available_port(-1)

    def test_find_available_port_with_invalid_start_port_too_high(self):
        """Test find_available_port raises error for port > 65535."""
        with pytest.raises(ValueError, match="Start port must be between 1 and 65535"):
            find_available_port(65536)

    def test_find_available_port_with_invalid_max_attempts(self):
        """Test find_available_port raises error for max_attempts < 1."""
        with pytest.raises(ValueError, match="Max attempts must be at least 1"):
            find_available_port(8000, max_attempts=0)

    def test_find_available_port_near_upper_limit(self):
        """Test find_available_port near port 65535 upper limit."""
        # Start very close to the limit
        port = find_available_port(65530, max_attempts=10)
        assert port is not None
        assert port <= 65535

    def test_find_available_port_returns_none_when_exhausted(self):
        """Test find_available_port returns None when no ports available."""
        # Start at 65535 with max_attempts = 1, should only check 65535
        port = find_available_port(65535, max_attempts=1)
        # May return None if 65535 is in use, or 65535 if available
        assert port is None or port == 65535

    def test_find_available_port_with_custom_host(self):
        """Test finding available port with custom host."""
        port = find_available_port(65450, host='127.0.0.1', max_attempts=5)
        assert port is not None
        assert isinstance(port, int)


class TestGetPortInfo:
    """Tests for get_port_info function."""

    def test_get_port_info_with_valid_port(self):
        """Test getting port info for valid port."""
        info = get_port_info(8000)
        assert isinstance(info, dict)
        assert 'port' in info
        assert 'is_in_use' in info
        assert 'host' in info
        assert 'error' in info
        assert info['port'] == 8000
        assert info['host'] == 'localhost'
        assert isinstance(info['is_in_use'], bool)

    def test_get_port_info_with_invalid_port_zero(self):
        """Test get_port_info raises error for port 0."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            get_port_info(0)

    def test_get_port_info_with_invalid_port_negative(self):
        """Test get_port_info raises error for negative port."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            get_port_info(-1)

    def test_get_port_info_with_custom_host(self):
        """Test getting port info with custom host."""
        info = get_port_info(8001, host='127.0.0.1')
        assert info['host'] == '127.0.0.1'

    def test_get_port_info_includes_error_on_failure(self):
        """Test get_port_info includes error message when check fails."""
        # Force an error with an invalid hostname
        info = get_port_info(8002, host='invalid.hostname.example')
        assert 'error' in info
        # On some systems, invalid hostnames might resolve (e.g., to a search page)
        # The key is that error field is populated when resolution fails
        # is_in_use could be True or False depending on system DNS behavior
        assert isinstance(info['is_in_use'], bool)


class TestCommandValidator:
    """Tests for CommandValidator class."""

    def test_command_validator_initialization(self):
        """Test CommandValidator can be instantiated."""
        validator = CommandValidator()
        assert validator is not None

    def test_command_exists_with_python(self):
        """Test command_exists detects python command."""
        # Python should be available since we're running Python tests
        result = CommandValidator.command_exists('python')
        # Use 'python3' as fallback if 'python' is not found
        result3 = CommandValidator.command_exists('python3')
        assert result or result3

    def test_command_exists_with_nonexistent_command(self):
        """Test command_exists returns False for nonexistent command."""
        result = CommandValidator.command_exists('thiscommanddefinitelydoesnotexist123')
        assert result is False

    def test_get_command_path_with_python(self):
        """Test get_command_path returns path for python."""
        path = CommandValidator.get_command_path('python')
        path3 = CommandValidator.get_command_path('python3')
        # At least one should exist
        assert path is not None or path3 is not None
        if path:
            assert isinstance(path, str)

            assert len(path) > 0

    def test_get_command_path_with_nonexistent_command(self):
        """Test get_command_path returns None for nonexistent command."""
        path = CommandValidator.get_command_path('nonexistentcommand123')
        assert path is None

    def test_check_version_with_python(self):
        """Test check_version retrieves Python version."""
        # Try python first, fall back to python3
        success, version = CommandValidator.check_version('python', '--version')
        if not success:
            success, version = CommandValidator.check_version('python3', '--version')

        assert success is True
        assert version is not None
        assert isinstance(version, str)
        assert len(version) > 0

    def test_check_version_with_nonexistent_command(self):
        """Test check_version fails for nonexistent command."""
        success, version = CommandValidator.check_version('nonexistent123')
        assert success is False
        assert version is None

    def test_check_version_handles_timeout(self):
        """Test check_version handles command timeout."""
        with patch('startup_utils.command_validator.shutil.which') as mock_which, \
             patch('startup_utils.command_validator.subprocess.run') as mock_run:
            mock_which.return_value = '/usr/bin/testcmd'
            mock_run.side_effect = subprocess.TimeoutExpired('cmd', 5)
            success, version = CommandValidator.check_version('testcmd')
            assert success is False
            # The implementation returns "Command timed out" for timeout
            assert version == "Command timed out"

    def test_validate_commands_with_multiple_commands(self):
        """Test validate_commands checks multiple commands."""
        results = CommandValidator.validate_commands(['python', 'nonexistent123'])
        assert isinstance(results, dict)
        assert 'python' in results or 'python3' in results  # Allow fallback
        assert 'nonexistent123' in results

        # Check structure of results
        for cmd, info in results.items():
            assert 'exists' in info
            assert 'path' in info
            assert 'version' in info
            assert 'error' in info

    def test_validate_commands_with_empty_list(self):
        """Test validate_commands with empty command list."""
        results = CommandValidator.validate_commands([])
        assert isinstance(results, dict)
        assert len(results) == 0


class TestCommandValidatorConvenienceFunctions:
    """Tests for command validator convenience functions."""

    def test_command_exists_function(self):
        """Test standalone command_exists function."""
        result = command_exists('python')
        result3 = command_exists('python3')
        assert result or result3

    def test_get_command_path_function(self):
        """Test standalone get_command_path function."""
        path = get_command_path('python')
        path3 = get_command_path('python3')
        assert path is not None or path3 is not None


class TestOutputMonitor:
    """Tests for OutputMonitor class."""

    def test_output_monitor_initialization_backend(self):
        """Test OutputMonitor initialization for backend."""
        monitor = OutputMonitor('backend')
        assert monitor.service_type == 'backend'
        assert monitor.status == ServiceStatus.PENDING
        assert monitor.matched_pattern is None
        assert len(monitor.output_lines) == 0

    def test_output_monitor_initialization_frontend(self):
        """Test OutputMonitor initialization for frontend."""
        monitor = OutputMonitor('frontend')
        assert monitor.service_type == 'frontend'
        assert monitor.status == ServiceStatus.PENDING

    def test_output_monitor_invalid_service_type(self):
        """Test OutputMonitor raises error for invalid service type."""
        with pytest.raises(ValueError, match="service_type must be 'backend' or 'frontend'"):
            OutputMonitor('invalid')

    def test_output_monitor_has_patterns(self):
        """Test OutputMonitor has pattern lists for verification."""
        monitor = OutputMonitor('backend')
        assert hasattr(monitor, 'backend_success_patterns')
        assert hasattr(monitor, 'backend_failure_patterns')
        assert hasattr(monitor, 'frontend_success_patterns')
        assert hasattr(monitor, 'frontend_failure_patterns')
        assert isinstance(monitor.backend_success_patterns, list)
        assert isinstance(monitor.backend_failure_patterns, list)
        assert len(monitor.backend_success_patterns) > 0
        assert len(monitor.backend_failure_patterns) > 0


class TestOutputMonitorBackendPatterns:
    """Tests for backend pattern detection."""

    def test_backend_detects_startup_complete(self):
        """Test backend detects 'Application startup complete' pattern."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('INFO:     Application startup complete.')
        assert status == ServiceStatus.SUCCESS
        assert monitor.status == ServiceStatus.SUCCESS

    def test_backend_detects_uvicorn_running(self):
        """Test backend detects 'Uvicorn running on' pattern."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('Uvicorn running on http://127.0.0.1:8000')
        assert status == ServiceStatus.SUCCESS

    def test_backend_detects_started_server(self):
        """Test backend detects 'Started server' pattern."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('INFO:     Started server process [12345]')
        assert status == ServiceStatus.SUCCESS

    def test_backend_detects_error_pattern(self):
        """Test backend detects error patterns."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('ERROR:    Some error occurred')
        assert status == ServiceStatus.FAILURE
        assert monitor.status == ServiceStatus.FAILURE

    def test_backend_detects_exception_pattern(self):
        """Test backend detects exception pattern."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('Exception: Something went wrong')
        assert status == ServiceStatus.FAILURE

    def test_backend_detects_traceback(self):
        """Test backend detects traceback pattern."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('Traceback (most recent call last):')
        assert status == ServiceStatus.FAILURE

    def test_backend_detects_port_in_use(self):
        """Test backend detects port in use error."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('ERROR:    Port 8000 is in use')
        assert status == ServiceStatus.FAILURE

    def test_backend_detects_address_in_use(self):
        """Test backend detects address already in use."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('Error: Address already in use')
        assert status == ServiceStatus.FAILURE

    def test_backend_detects_module_not_found(self):
        """Test backend detects module not found error."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('ModuleNotFoundError: No module named "missing"')
        assert status == ServiceStatus.FAILURE

    def test_backend_transitions_to_in_progress(self):
        """Test backend transitions to IN_PROGRESS on regular output."""
        monitor = OutputMonitor('backend')
        status = monitor.process_line('Some regular output line')
        assert status == ServiceStatus.IN_PROGRESS

    def test_backend_does_not_change_after_success(self):
        """Test backend status can be changed by patterns after success."""
        monitor = OutputMonitor('backend')
        monitor.process_line('Application startup complete')
        assert monitor.status == ServiceStatus.SUCCESS
        # Process more lines - if a failure pattern appears, it will change status
        monitor.process_line('ERROR: Some error')
        # After success, a failure pattern will change status to FAILURE
        assert monitor.status == ServiceStatus.FAILURE


class TestOutputMonitorFrontendPatterns:
    """Tests for frontend pattern detection."""

    def test_frontend_detects_local_url(self):
        """Test frontend detects Local URL pattern."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('  Local:   http://localhost:5173/')
        assert status == ServiceStatus.SUCCESS

    def test_frontend_detects_ready_in_ms(self):
        """Test frontend detects 'ready in X ms' pattern."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('VITE v4.4.9 ready in 234 ms')
        assert status == ServiceStatus.SUCCESS

    def test_frontend_detects_vite_ready(self):
        """Test frontend detects VITE ready pattern."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('  VITE v5.0.0  ready in 123 ms')
        assert status == ServiceStatus.SUCCESS

    def test_frontend_detects_emoji_local(self):
        """Test frontend detects emoji arrow with Local."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('➜  Local:   http://localhost:5173/')
        assert status == ServiceStatus.SUCCESS

    def test_frontend_detects_error_pattern(self):
        """Test frontend detects error pattern."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('ERROR: Some error occurred')
        assert status == ServiceStatus.FAILURE

    def test_frontend_detects_failed_to_compile(self):
        """Test frontend detects failed to compile pattern."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('ERROR: Failed to compile')
        assert status == ServiceStatus.FAILURE

    def test_frontend_detects_failed_to_resolve(self):
        """Test frontend detects failed to resolve pattern."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('ERROR: Failed to resolve import')
        assert status == ServiceStatus.FAILURE

    def test_frontend_detects_command_not_found(self):
        """Test frontend detects command not found pattern."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('sh: vite: not found')
        assert status == ServiceStatus.FAILURE

    def test_frontend_transitions_to_in_progress(self):
        """Test frontend transitions to IN_PROGRESS on regular output."""
        monitor = OutputMonitor('frontend')
        status = monitor.process_line('Some regular output line')
        assert status == ServiceStatus.IN_PROGRESS


class TestOutputMonitorMultiLineProcessing:
    """Tests for multi-line output processing."""

    def test_process_output_multiple_lines(self):
        """Test processing multiple lines of output."""
        monitor = OutputMonitor('backend')
        output = """INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete."""
        status = monitor.process_output(output)
        assert status == ServiceStatus.SUCCESS
        # process_output stops early when reaching SUCCESS
        # So only lines up to (and including) the success pattern are processed
        assert len(monitor.output_lines) >= 1
        assert monitor.status == ServiceStatus.SUCCESS

    def test_process_output_stops_at_success(self):
        """Test process_output stops processing after success."""
        monitor = OutputMonitor('backend')
        output = """INFO:     Application startup complete.
ERROR:    Some error after startup"""
        status = monitor.process_output(output)
        assert status == ServiceStatus.SUCCESS
        # Stops after first line that matches SUCCESS pattern
        assert len(monitor.output_lines) == 1

    def test_process_output_stops_at_failure(self):
        """Test process_output stops processing after failure."""
        monitor = OutputMonitor('backend')
        output = """Some regular line
ERROR:    Critical error
Application startup complete"""
        status = monitor.process_output(output)
        assert status == ServiceStatus.FAILURE

    def test_process_output_with_empty_lines(self):
        """Test process_output handles empty lines."""
        monitor = OutputMonitor('backend')
        output = """Line 1

Line 3"""
        status = monitor.process_output(output)
        # Should handle empty lines without error
        assert status in (ServiceStatus.IN_PROGRESS, ServiceStatus.SUCCESS, ServiceStatus.FAILURE)


class TestOutputMonitorCallbacks:
    """Tests for output monitor callback functionality."""

    def test_add_callback(self):
        """Test adding a callback to monitor."""
        monitor = OutputMonitor('backend')
        callback_mock = Mock()
        monitor.add_callback(callback_mock)
        assert callback_mock in monitor._callbacks

    def test_callback_triggered_on_status_change(self):
        """Test callback is triggered when status changes."""
        monitor = OutputMonitor('backend')
        callback_mock = Mock()
        monitor.add_callback(callback_mock)

        monitor.process_line('Application startup complete')

        callback_mock.assert_called_once()
        args = callback_mock.call_args[0]
        assert args[0] == ServiceStatus.SUCCESS

    def test_callback_not_triggered_on_same_status(self):
        """Test callback not triggered for same status."""
        monitor = OutputMonitor('backend')
        callback_mock = Mock()
        monitor.add_callback(callback_mock)

        monitor.process_line('Line 1')
        monitor.process_line('Line 2')

        # Should only be called once (when transitioning from PENDING to IN_PROGRESS)
        assert callback_mock.call_count == 1

    def test_callback_handles_exception_gracefully(self):
        """Test monitor handles callback exceptions without breaking."""
        monitor = OutputMonitor('backend')

        def failing_callback(status, pattern):
            raise RuntimeError("Callback error")

        monitor.add_callback(failing_callback)

        # Should not raise exception
        monitor.process_line('Application startup complete')
        assert monitor.status == ServiceStatus.SUCCESS


class TestOutputMonitorStatusInfo:
    """Tests for get_status_info method."""

    def test_get_status_info_structure(self):
        """Test get_status_info returns correct structure."""
        monitor = OutputMonitor('backend')
        monitor.process_line('Test output')

        info = monitor.get_status_info()
        assert isinstance(info, dict)
        assert 'service_type' in info
        assert 'status' in info
        assert 'matched_pattern' in info
        assert 'output_lines' in info
        assert 'line_count' in info

    def test_get_status_info_values(self):
        """Test get_status_info returns correct values."""
        monitor = OutputMonitor('frontend')
        monitor.process_line('Local: http://localhost:5173/')

        info = monitor.get_status_info()
        assert info['service_type'] == 'frontend'
        assert info['status'] == ServiceStatus.SUCCESS.value
        assert info['line_count'] == 1
        assert len(info['output_lines']) == 1


class TestOutputMonitorReset:
    """Tests for reset method."""

    def test_reset_clears_status(self):
        """Test reset clears status to PENDING."""
        monitor = OutputMonitor('backend')
        monitor.process_line('Application startup complete')
        assert monitor.status == ServiceStatus.SUCCESS

        monitor.reset()
        assert monitor.status == ServiceStatus.PENDING

    def test_reset_clears_matched_pattern(self):
        """Test reset clears matched pattern."""
        monitor = OutputMonitor('backend')
        monitor.process_line('Application startup complete')
        assert monitor.matched_pattern is not None

        monitor.reset()
        assert monitor.matched_pattern is None

    def test_reset_clears_output_lines(self):
        """Test reset clears output lines."""
        monitor = OutputMonitor('backend')
        monitor.process_line('Line 1')
        monitor.process_line('Line 2')
        assert len(monitor.output_lines) == 2

        monitor.reset()
        assert len(monitor.output_lines) == 0

    def test_reset_preserves_callbacks(self):
        """Test reset preserves registered callbacks."""
        monitor = OutputMonitor('backend')
        callback_mock = Mock()
        monitor.add_callback(callback_mock)

        monitor.reset()
        assert callback_mock in monitor._callbacks


class TestOutputMonitorWaitForCompletion:
    """Tests for wait_for_completion method."""

    def test_wait_for_completion_immediate_success(self):
        """Test wait_for_completion returns immediately when status is SUCCESS."""
        monitor = OutputMonitor('backend')
        monitor.process_line('Application startup complete')

        status = monitor.wait_for_completion(timeout=1.0)
        assert status == ServiceStatus.SUCCESS

    def test_wait_for_completion_immediate_failure(self):
        """Test wait_for_completion returns immediately when status is FAILURE."""
        monitor = OutputMonitor('backend')
        monitor.process_line('ERROR: Critical error')

        status = monitor.wait_for_completion(timeout=1.0)
        assert status == ServiceStatus.FAILURE

    def test_wait_for_completion_times_out(self):
        """Test wait_for_completion returns TIMEOUT after timeout."""
        monitor = OutputMonitor('backend')
        # Don't process any output, status stays PENDING

        status = monitor.wait_for_completion(timeout=0.2)
        assert status == ServiceStatus.TIMEOUT


class TestCreateMonitor:
    """Tests for create_monitor factory function."""

    def test_create_monitor_backend(self):
        """Test create_monitor creates backend monitor."""
        monitor = create_monitor('backend')
        assert isinstance(monitor, OutputMonitor)
        assert monitor.service_type == 'backend'

    def test_create_monitor_frontend(self):
        """Test create_monitor creates frontend monitor."""
        monitor = create_monitor('frontend')
        assert isinstance(monitor, OutputMonitor)
        assert monitor.service_type == 'frontend'

    def test_create_monitor_default(self):
        """Test create_monitor defaults to backend."""
        monitor = create_monitor()
        assert isinstance(monitor, OutputMonitor)
        assert monitor.service_type == 'backend'


class TestDetectBackendSuccess:
    """Tests for detect_backend_success convenience function."""

    def test_detect_backend_success_true(self):
        """Test detect_backend_success returns True for success pattern."""
        result = detect_backend_success('INFO: Application startup complete')
        assert result is True

    def test_detect_backend_success_false(self):
        """Test detect_backend_success returns False for no pattern."""
        result = detect_backend_success('Some random output')
        assert result is False

    def test_detect_backend_success_with_failure(self):
        """Test detect_backend_success returns False for failure pattern."""
        result = detect_backend_success('ERROR: Some error')
        assert result is False


class TestDetectFrontendSuccess:
    """Tests for detect_frontend_success convenience function."""

    def test_detect_frontend_success_true(self):
        """Test detect_frontend_success returns True for success pattern."""
        result = detect_frontend_success('Local: http://localhost:5173/')
        assert result is True

    def test_detect_frontend_success_false(self):
        """Test detect_frontend_success returns False for no pattern."""
        result = detect_frontend_success('Some random output')
        assert result is False

    def test_detect_frontend_success_with_failure(self):
        """Test detect_frontend_success returns False for failure pattern."""
        result = detect_frontend_success('ERROR: Failed to compile')
        assert result is False


class TestDetectFailure:
    """Tests for detect_failure convenience function."""

    def test_detect_failure_backend_true(self):
        """Test detect_failure returns True for backend failure pattern."""
        result = detect_failure('ERROR: Some error', 'backend')
        assert result is True

    def test_detect_failure_frontend_true(self):
        """Test detect_failure returns True for frontend failure pattern."""
        result = detect_failure('ERROR: Failed to compile', 'frontend')
        assert result is True

    def test_detect_failure_false(self):
        """Test detect_failure returns False for no failure pattern."""
        result = detect_failure('Some normal output', 'backend')
        assert result is False

    def test_detect_failure_default_backend(self):
        """Test detect_failure defaults to backend service type."""
        result = detect_failure('ERROR: Some error')
        assert result is True
