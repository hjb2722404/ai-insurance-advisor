#!/bin/bash
echo "Starting AI Insurance Advisor - Local Development Environment"
echo ""

echo "[1/2] Starting Backend (FastAPI) on http://localhost:8000"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

echo "[2/2] Starting Frontend (uni-app H5) ..."
cd frontend && npm run dev:h5 &
FRONTEND_PID=$!

echo ""
echo "Both services started. PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
