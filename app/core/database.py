"""Database core module.

This module provides the SQLAlchemy base class, engine initialization, 
and session factory for the application.
"""

import logging
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from app.core.config import settings

logger = logging.getLogger(__name__)

@as_declarative()
class Base:
    """Base class for all SQLAlchemy models.

    Automatically generates table names based on the class name unless 
    explicitly overridden in the child class.

    Attributes:
        id: The primary key of the model.
        __name__: The name of the class.
    """
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Converts the class name to lowercase to use as the database table name.

        Returns:
            str: The generated table name.
        """
        return cls.__name__.lower()


def get_db_engine():
    """Creates the SQLAlchemy database engine.

    Uses pool_pre_ping to ensure connections are valid before use and 
    sets a connection timeout.

    Returns:
        sqlalchemy.engine.Engine: The initialized SQLAlchemy engine.
    """
    return create_engine(
        settings.database_url, 
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10}
    )


# Global engine and SessionLocal initialization
try:
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    # Basic print for critical early failure
    print(f"FATAL: Application failed to initialize database configuration: {e}")
    raise
