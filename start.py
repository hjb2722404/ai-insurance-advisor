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
import sys
from pathlib import Path
from typing import Optional

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

    # TODO: Subtask 4-2 - Implement concurrent service startup
    # TODO: Subtask 4-3 - Implement signal handling
    print_warning("Service startup not yet implemented - see subtask 4-2")

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
