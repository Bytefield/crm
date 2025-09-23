"""
Base model definitions for SQLAlchemy models.

This module contains the base class that all SQLAlchemy models should inherit from.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func

# Create a base class for models
Base = declarative_base()

class BaseModel:
    """Base model with common fields and methods.
    
    All models should inherit from this class to get common fields like id,
    created_at, and updated_at.
    """
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
