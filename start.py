#!/usr/bin/env python
"""
AI Insurance Advisor - Main Startup Script

This is the main entry point for starting both the backend (FastAPI) and
frontend (Vue/uni-app) services with intelligent port management and
automatic dependency installation.

Features:
- Automatic port conflict detection and resolution
- Command validation and auto-installation of missing dependencies
- Concurrent service startup with output monitoring
- Color-coded console output for clear status communication
- Graceful shutdown on Ctrl+C

Usage:
    python start.py [options]

Options:
    --help              Show this help message and exit
    --dry-run           Show what would happen without executing
    --backend-port      Specify backend port (default: auto-detect)
    --frontend-port     Specify frontend port (default: auto-detect)
    --verbose           Enable verbose output
    --no-backend        Skip starting the backend service
    --no-frontend       Skip starting the frontend service
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Optional

# Add startup_utils to path
sys.path.insert(0, str(Path(__file__).parent))

from startup_utils import (
    BackendStarter,
    FrontendStarter,
    create_backend_starter,
    create_frontend_starter,
)


class Colors:
    """ANSI color codes for terminal output.

    Provides color constants for formatted console output across
    different platforms. Automatically detects if colors are supported.
    """

    # ANSI color codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    @staticmethod
    def supports_color() -> bool:
        """Check if the terminal supports color output.

        Returns:
            True if the terminal supports colors, False otherwise.
        """
        # Check if we're running in a terminal
        if not hasattr(sys.stdout, 'isatty'):
            return False

        if not sys.stdout.isatty():
            return False

        # Check for Windows
        if os.name == 'nt':
            # Windows 10+ supports ANSI colors
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                return False

        # Unix-like systems generally support colors
        return True

    @classmethod
    def strip(cls, text: str) -> str:
        """Remove ANSI color codes from text.

        Args:
            text: The text to strip colors from.

        Returns:
            The text without ANSI color codes.
        """
        import re
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', text)


class ColoredFormatter(logging.Formatter):
    """Custom logging formatter with color support.

    Formats log messages with appropriate colors based on their level.
    """

    # Color mapping for log levels
    LEVEL_COLORS = {
        logging.DEBUG: Colors.DIM,
        logging.INFO: Colors.CYAN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BG_RED + Colors.WHITE,
    }

    def __init__(self, use_color: Optional[bool] = None, **kwargs):
        """
        Initialize the colored formatter.

        Args:
            use_color: Whether to use colors. If None, auto-detects.
            **kwargs: Additional arguments to pass to logging.Formatter.
        """
        super().__init__(**kwargs)
        if use_color is None:
            self.use_color = Colors.supports_color()
        else:
            self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with appropriate colors.

        Args:
            record: The log record to format.

        Returns:
            The formatted log message.
        """
        # Format the base message
        message = super().format(record)

        # Add colors if enabled
        if self.use_color:
            color = self.LEVEL_COLORS.get(record.levelno, '')
            reset = Colors.RESET if color else ''
            message = f"{color}{message}{reset}"

        return message


def print_info(message: str) -> None:
    """Print an informational message in cyan.

    Args:
        message: The message to print.
    """
    if Colors.supports_color():
        print(f"{Colors.CYAN}{message}{Colors.RESET}")
    else:
        print(message)


def print_success(message: str) -> None:
    """Print a success message in green.

    Args:
        message: The message to print.
    """
    if Colors.supports_color():
        print(f"{Colors.GREEN}{message}{Colors.RESET}")
    else:
        print(message)


def print_warning(message: str) -> None:
    """Print a warning message in yellow.

    Args:
        message: The message to print.
    """
    if Colors.supports_color():
        print(f"{Colors.YELLOW}{message}{Colors.RESET}")
    else:
        print(message)


def print_error(message: str) -> None:
    """Print an error message in red.

    Args:
        message: The message to print.
    """
    if Colors.supports_color():
        print(f"{Colors.RED}{message}{Colors.RESET}")
    else:
        print(message)


def print_header(message: str) -> None:
    """Print a header message in bold blue.

    Args:
        message: The message to print.
    """
    if Colors.supports_color():
        print(f"\n{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}\n")
    else:
        print(f"\n{message}\n")


class ServiceManager:
    """Manages concurrent service startup and shutdown.

    Handles starting multiple services concurrently, monitoring their output,
    and providing graceful shutdown when requested.
    """

    def __init__(self, logger: logging.Logger):
        """Initialize the service manager.

        Args:
            logger: Logger instance for output messages.
        """
        self.logger = logger
        self.processes: Dict[str, subprocess.Popen] = {}
        self.output_threads: Dict[str, threading.Thread] = {}
        self.shutdown_event = threading.Event()
        self._lock = threading.Lock()

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals (SIGINT, SIGTERM).

        Args:
            signum: The signal number received.
            frame: The current stack frame.
        """
        sig_name = signal.Signals(signum).name
        self.logger.info(f"Received {sig_name}, shutting down services...")
        self.shutdown_event.set()
        self.stop_all()

    def _read_output(self, process: subprocess.Popen, service_name: str,
                     prefix: str, color_code: str) -> None:
        """Read and print process output in real-time.

        Args:
            process: The subprocess to read output from.
            service_name: Name of the service for logging.
            prefix: Prefix to add to each line of output.
            color_code: ANSI color code for the output.
        """
        reset_code = Colors.RESET if color_code else ''
        try:
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    # Strip the newline and add our formatting
                    line = line.rstrip('\n\r')
                    if Colors.supports_color():
                        print(f"{color_code}{prefix}{line}{reset_code}")
                    else:
                        print(f"{prefix}{line}")
        except Exception as e:
            self.logger.debug(f"Error reading {service_name} output: {e}")

    def start_service(self, service_name: str, command: list[str],
                      cwd: Path, prefix: str, color_code: str) -> Optional[subprocess.Popen]:
        """Start a service and begin monitoring its output.

        Args:
            service_name: Name identifier for the service.
            command: Command list to execute.
            cwd: Working directory for the process.
            prefix: Prefix for output lines (e.g., "[Backend] ").
            color_code: ANSI color code for output.

        Returns:
            The subprocess.Popen object if started successfully, None otherwise.
        """
        if self.shutdown_event.is_set():
            self.logger.warning(f"Shutdown in progress, skipping {service_name}")
            return None

        try:
            self.logger.info(f"Starting {service_name}...")

            # Start the process
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                stdin=subprocess.DEVNULL,
            )

            with self._lock:
                self.processes[service_name] = process

            # Start output monitoring thread
            output_thread = threading.Thread(
                target=self._read_output,
                args=(process, service_name, prefix, color_code),
                daemon=True,
                name=f"{service_name}-output"
            )
            output_thread.start()
            self.output_threads[service_name] = output_thread

            self.logger.debug(f"{service_name} started with PID {process.pid}")
            return process

        except Exception as e:
            self.logger.error(f"Failed to start {service_name}: {e}")
            return None

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service.

        Args:
            service_name: Name of the service to stop.

        Returns:
            True if the service was stopped, False otherwise.
        """
        with self._lock:
            process = self.processes.get(service_name)
            if not process:
                self.logger.debug(f"Service {service_name} not found")
                return False

            try:
                if process.poll() is None:
                    self.logger.info(f"Stopping {service_name} (PID {process.pid})...")
                    process.terminate()

                    # Wait up to 5 seconds for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.logger.warning(
                            f"{service_name} did not shut down gracefully, forcing..."
                        )
                        process.kill()
                        process.wait()

                # Remove from tracking
                del self.processes[service_name]
                return True

            except Exception as e:
                self.logger.error(f"Error stopping {service_name}: {e}")
                return False

    def stop_all(self) -> None:
        """Stop all running services."""
        with self._lock:
            service_names = list(self.processes.keys())

        if not service_names:
            return

        self.logger.info("Stopping all services...")

        # Stop each service
        for service_name in service_names:
            self.stop_service(service_name)

        # Wait for output threads to finish
        for service_name, thread in self.output_threads.items():
            if thread.is_alive():
                thread.join(timeout=2)

        self.logger.info("All services stopped")

    def wait_for_services(self, timeout: Optional[float] = None) -> Dict[str, int]:
        """Wait for all services to complete or timeout.

        Args:
            timeout: Maximum time to wait in seconds. None for unlimited.

        Returns:
            Dictionary mapping service names to their exit codes.
        """
        exit_codes = {}
        start_time = time.time()

        while True:
            # Check if shutdown was requested
            if self.shutdown_event.is_set():
                break

            # Check if all processes have completed
            all_done = True
            with self._lock:
                for name, process in self.processes.items():
                    if process.poll() is None:
                        all_done = False
                        break
                    else:
                        exit_codes[name] = process.returncode

            if all_done:
                break

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                self.logger.warning("Timeout reached, stopping services...")
                self.stop_all()
                break

            # Small sleep to avoid busy waiting
            time.sleep(0.1)

        return exit_codes

    def get_pids(self) -> Dict[str, int]:
        """Get PIDs of all running services.

        Returns:
            Dictionary mapping service names to their PIDs.
        """
        pids = {}
        with self._lock:
            for name, process in self.processes.items():
                if process.poll() is None:
                    pids[name] = process.pid
        return pids


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration for the startup script.

    Args:
        verbose: Whether to enable verbose (DEBUG level) logging.
        log_file: Optional path to a log file. If None, no file logging.

    Returns:
        The configured logger instance.
    """
    # Create logger
    logger = logging.getLogger('start')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = ColoredFormatter(
        fmt='%(levelname)s: %(message)s',
        use_color=True
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        The parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog='start.py',
        description='AI Insurance Advisor - Service startup script with port management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py                 Start both services (auto-detect ports)
  python start.py --dry-run       Show what would happen without starting
  python start.py --backend-port 8001 --frontend-port 5174
  python start.py --no-backend    Start only frontend
  python start.py --verbose       Enable verbose output
        """
    )

    # Port configuration
    parser.add_argument(
        '--backend-port',
        type=int,
        metavar='PORT',
        help='Backend port (default: 8000, or auto-increment if occupied)'
    )
    parser.add_argument(
        '--frontend-port',
        type=int,
        metavar='PORT',
        help='Frontend port (default: 5173, or auto-increment if occupied)'
    )

    # Service selection
    parser.add_argument(
        '--no-backend',
        action='store_true',
        help='Skip starting the backend service'
    )
    parser.add_argument(
        '--no-frontend',
        action='store_true',
        help='Skip starting the frontend service'
    )

    # Mode options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without executing commands'
    )

    # Output options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        metavar='FILE',
        default='startup.log',
        help='Log file path (default: startup.log)'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    parser.add_argument(
        '--no-log',
        action='store_true',
        help='Disable file logging'
    )

    return parser.parse_args()


def print_startup_banner() -> None:
    """Print the startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         AI Insurance Advisor - Local Development             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    if Colors.supports_color():
        print(f"{Colors.BOLD}{Colors.CYAN}{banner}{Colors.RESET}")
    else:
        print(banner)


def main() -> int:
    """Main entry point for the startup script.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Parse arguments
    args = parse_arguments()

    # Disable color if requested
    if args.no_color:
        # Override color functions with plain versions
        global print_info, print_success, print_warning, print_error, print_header
        def print_info(message: str) -> None: print(f"INFO: {message}")
        def print_success(message: str) -> None: print(f"SUCCESS: {message}")
        def print_warning(message: str) -> None: print(f"WARNING: {message}")
        def print_error(message: str) -> None: print(f"ERROR: {message}", file=sys.stderr)
        def print_header(message: str) -> None: print(f"\n{'='*60}\n{message}\n{'='*60}\n")

    # Set up logging
    log_file = None if args.no_log else args.log_file
    logger = setup_logging(verbose=args.verbose, log_file=log_file)

    # Print startup banner
    print_startup_banner()

    # Show dry-run mode
    if args.dry_run:
        print_warning("Dry run mode - no services will be started")

    # Get project root
    project_root = Path.cwd()
    logger.debug(f"Project root: {project_root}")

    # Initialize service starters
    backend_starter: Optional[BackendStarter] = None
    frontend_starter: Optional[FrontendStarter] = None

    if not args.no_backend:
        backend_port = args.backend_port
        backend_starter = create_backend_starter(
            project_root=project_root,
            default_port=backend_port
        )
        print_header("[1/2] Backend Service Configuration")
        print_info(f"Backend directory: {backend_starter.backend_dir}")
        print_info(f"Default port: {backend_starter.default_port}")

    if not args.no_frontend:
        frontend_port = args.frontend_port
        frontend_starter = create_frontend_starter(
            project_root=project_root,
            default_port=frontend_port
        )
        print_header("[2/2] Frontend Service Configuration")
        print_info(f"Frontend directory: {frontend_starter.frontend_dir}")
        print_info(f"Default port: {frontend_starter.default_port}")

    # In dry-run mode, just show what would happen
    if args.dry_run:
        print_header("Dry Run Summary")
        if not args.no_backend:
            port = backend_starter.get_available_port() if backend_starter else "N/A"
            print_info(f"Backend would start on port: {port}")
        if not args.no_frontend:
            port = frontend_starter.get_available_port() if frontend_starter else "N/A"
            print_info(f"Frontend would start on port: {port}")
        return 0

    # Start services concurrently
    print_header("Starting Services")

    # Create service manager
    manager = ServiceManager(logger)

    # Backend service
    if backend_starter:
        try:
            # Find available port
            backend_port = backend_starter.get_available_port()
            logger.info(f"Backend port: {backend_port}")

            # Build command
            backend_cmd = backend_starter.get_start_command(port=backend_port)

            # Start backend
            backend_process = manager.start_service(
                service_name="Backend",
                command=backend_cmd,
                cwd=backend_starter.backend_dir,
                prefix="[Backend] ",
                color_code=Colors.MAGENTA
            )

            if backend_process:
                print_success(f"Backend started on http://localhost:{backend_port}")
                print_success(f"API Docs: http://localhost:{backend_port}/docs")
            else:
                print_error("Failed to start backend")
                return 1

        except Exception as e:
            print_error(f"Error starting backend: {e}")
            logger.debug(f"Backend error details:", exc_info=True)
            return 1

    # Small delay before starting frontend (like start-dev.sh)
    if backend_starter and frontend_starter:
        time.sleep(2)

    # Frontend service
    if frontend_starter:
        try:
            # Find available port
            frontend_port = frontend_starter.get_available_port()
            logger.info(f"Frontend port: {frontend_port}")

            # Build command
            frontend_cmd = frontend_starter.get_start_command(port=frontend_port)

            # Start frontend
            frontend_process = manager.start_service(
                service_name="Frontend",
                command=frontend_cmd,
                cwd=frontend_starter.frontend_dir,
                prefix="[Frontend] ",
                color_code=Colors.BLUE
            )

            if frontend_process:
                print_success(f"Frontend started on http://localhost:{frontend_port}")
            else:
                print_error("Failed to start frontend")
                # Stop backend if running
                if backend_starter:
                    manager.stop_all()
                return 1

        except Exception as e:
            print_error(f"Error starting frontend: {e}")
            logger.debug(f"Frontend error details:", exc_info=True)
            if backend_starter:
                manager.stop_all()
            return 1

    # Show service status
    pids = manager.get_pids()
    if pids:
        print_header("Services Running")
        pid_list = ", ".join(f"{name}={pid}" for name, pid in pids.items())
        print_info(f"PIDs: {pid_list}")

        print("\nService URLs:")
        if "Backend" in pids and backend_starter:
            port = backend_starter.get_available_port()
            print(f"  - Backend:    http://localhost:{port}")
            print(f"  - API Docs:   http://localhost:{port}/docs")
        if "Frontend" in pids and frontend_starter:
            port = frontend_starter.get_available_port()
            print(f"  - Frontend:   http://localhost:{port}")
        print()

    print_info("Press Ctrl+C to stop all services")

    # Wait for services (indefinitely until Ctrl+C)
    exit_codes = manager.wait_for_services()

    # Report exit codes if services stopped on their own
    if exit_codes:
        logger.info("Service exit codes:")
        for name, code in exit_codes.items():
            logger.info(f"  {name}: {code}")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_info("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
