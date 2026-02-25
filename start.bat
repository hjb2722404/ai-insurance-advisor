@echo off
REM AI Insurance Advisor - Main Startup Script Wrapper
REM This script wraps start.py for Windows systems

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%" || exit /b 1

REM Call start.py with all arguments passed through
python start.py %*
