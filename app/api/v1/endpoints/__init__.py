"""
API endpoints package for the CRM application.

This package contains all the API endpoint modules for version 1 of the API.
"""

# Import all endpoint modules here to make them available when importing from .endpoints
from . import auth, users, campaigns, contacts

__all__ = ['auth', 'users', 'campaigns', 'contacts']
