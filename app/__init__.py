"""
CRM Application Package

This is the main package for the CRM application, containing all the core
functionality and API endpoints.
"""

# Import core components
from .core.config import settings
from .db import Base, SessionLocal, get_db
from .models import User, Campaign, Contact, CampaignStatus, CampaignContact

# Make these available when importing from app
__all__ = [
    'settings',
    'Base',
    'SessionLocal',
    'get_db',
    'User',
    'Campaign',
    'Contact',
    'CampaignStatus',
    'CampaignContact',
]
