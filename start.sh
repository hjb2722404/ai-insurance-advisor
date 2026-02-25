#!/bin/bash
# AI Insurance Advisor - Main Startup Script Wrapper
# This script wraps start.py for Unix/Linux/macOS systems

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR" || exit 1

# Call start.py with all arguments passed through
python start.py "$@"
