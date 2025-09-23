"""
API package for the CRM application.

This package contains all API-related code, including versioned API endpoints.
"""

__version__ = '0.1.0'

# Import API router
from app.api.v1.api import api_router as v1_router

__all__ = ['v1_router']
