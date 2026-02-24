"""
FastAPI Application Entry Point

Main application module for the AI Insurance Advisor API.
Configures FastAPI app with CORS middleware for frontend access.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Insurance Advisor API",
    description="AI-powered insurance consultation and contract interpretation service",
    version="0.1.0",
)

# Configure CORS middleware for frontend access
# CRITICAL: Must explicitly allow frontend origin to prevent CORS errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Insurance Advisor API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
