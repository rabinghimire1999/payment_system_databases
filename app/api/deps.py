"""FastAPI dependency injection module.

This module provides reusable dependencies for API routes, such as database sessions.
"""

import logging
from typing import Generator
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

def get_db() -> Generator:
    """Yields a database session to be used by FastAPI endpoints.

    Ensures that the session is properly closed after the request completes,
    and rolls back any pending transactions if an error occurs.

    Yields:
        Session: A SQLAlchemy database session.

    Raises:
        Exception: If an error occurs while creating or using the session, 
            it is logged and re-raised after rollback.
    """
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()
