@echo off
echo Starting AI Insurance Advisor - Local Development Environment
echo.

echo [1/2] Starting Backend (FastAPI) on http://localhost:8000
start "Backend" cmd /k "uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Frontend (uni-app H5) ...
start "Frontend" cmd /k "cd frontend && npm run dev:h5"

echo.
echo Both services starting in separate windows...
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window (services will continue running)
pause >nul
