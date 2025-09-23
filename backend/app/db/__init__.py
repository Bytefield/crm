"""
Database package for the CRM application.

This package contains database-related code, including session management
and base model definitions.
"""

from .session import SessionLocal, engine, get_db
from .base import Base

__all__ = ['SessionLocal', 'engine', 'get_db', 'Base']
