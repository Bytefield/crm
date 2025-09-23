from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get DB session.
    
    Yields:
        Session: A SQLAlchemy database session.
        
    Example:
        ```python
        from fastapi import Depends
        from .db.session import get_db
        
        @app.get("/items/")
        def read_items(db = Depends(get_db)):
            # Use the database session
            items = db.query(Item).all()
            return items
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
