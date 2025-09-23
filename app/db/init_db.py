from sqlalchemy import create_engine
from ..core.config import settings
from ..models.base import Base
from ..models import *  # Import all models to register them with SQLAlchemy

def init_db():
    """Initialize the database with tables."""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
