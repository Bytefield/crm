# This file makes the core directory a Python package

# Import settings to make them available when importing from app.core
from .config import settings

__all__ = ['settings']
