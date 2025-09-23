"""
API v1 package for the CRM application.

This package contains all version 1 API endpoints and related code.
"""

__version__ = '1.0.0'

# Import API router
from .api import api_router

__all__ = ['api_router']
