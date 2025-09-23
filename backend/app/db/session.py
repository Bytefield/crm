from fastapi import HTTPException, status
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator, TypeVar, Type, Any
import logging

from ..core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine with connection pooling and timeouts
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=5,         # Number of connections to keep open
    max_overflow=10,     # Max number of connections to create if pool is full
    connect_args={
        'connect_timeout': 10,  # Connection timeout in seconds
        'application_name': 'crm_backend',
    }
)

# Add event listeners for connection validation
@event.listens_for(engine, 'before_cursor_execute')
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    """Log and validate SQL statements before execution."""
    logger.debug("Executing SQL: %s", statement)
    
    # Basic SQL injection check (complementary to ORM-level protection)
    if any(keyword in statement.upper() for keyword in ['DROP', 'TRUNCATE', 'DELETE FROM', 'UPDATE', 'INSERT']):
        if not any(statement.upper().startswith(prefix) for prefix in ['UPDATE', 'INSERT', 'DELETE']):
            logger.warning("Potential SQL injection attempt detected: %s", statement)
            raise SQLAlchemyError("Invalid SQL operation detected")

# Create a configured "Session" class with security settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True
)

# Create a base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get a secure DB session.
    
    Yields:
        Session: A SQLAlchemy database session with security measures.
        
    Raises:
        HTTPException: If there's an error creating the session.
        
    """
    db = SessionLocal()
    try:
        # Set secure session parameters
        db.execute("SET SESSION statement_timeout = '30s'")
        db.execute("SET SESSION idle_in_transaction_session_timeout = '5min'")
        
        yield db
    except SQLAlchemyError as e:
        # Rollback on error
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
    finally:
        # Ensure the session is closed
        db.close()

# Secure query builder
def secure_query(model, db: Session, **filters):
    """
    Execute a secure database query with input validation.
    
    Args:
        model: SQLAlchemy model class
        db: Database session
        **filters: Filter conditions (column=value)
        
    Returns:
        Query: A SQLAlchemy query object
        
    Raises:
        HTTPException: If invalid filter fields are provided
    """
    # Validate model attributes
    valid_columns = {column.name for column in model.__table__.columns}
    
    # Check for invalid filter fields
    invalid_fields = set(filters.keys()) - valid_columns
    if invalid_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filter fields: {', '.join(invalid_fields)}"
        )
    
    # Build query with filters
    query = db.query(model)
    for column, value in filters.items():
        if value is not None:
            query = query.filter(getattr(model, column) == value)
    
    return query
