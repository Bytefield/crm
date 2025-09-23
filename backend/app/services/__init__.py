"""
Services package for the CRM application.

This package contains all the business logic and service layer components.
"""

# Import services to make them available when importing from app.services
from . import auth

__all__ = ['auth']
