"""
Main application module for the Social Campaign CRM API.

This module creates and configures the FastAPI application instance.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import using absolute paths
from app.core.config import settings
from app.api.v1.api import api_router

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Social Campaign CRM API",
        description="API for managing social campaigns and tracking attribution",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

# Create the FastAPI application
app = create_application()

@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to the Social Campaign CRM API"}
