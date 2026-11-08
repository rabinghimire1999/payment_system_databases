"""
API Key model module.

Defines the structure for storing and managing API keys associated with fpss.
"""
import uuid
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, func
# pyrefly: ignore [missing-import]
from sqlalchemy.dialects.postgresql import UUID
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.core.database import Base


class ApiKey(Base):
    """
    Model representing an API key for a fps.

    Used to authenticate requests from external integrations.

    Attributes:
        id (uuid.UUID): Primary key, unique identifier for the API key.
        fps_id (int): Foreign key referencing the fps.
        hashed_key (str): The hashed version of the API key for security.
        is_active (bool): Whether the API key is currently valid.
        created_at (datetime): Timestamp when the key was generated.
        fps (fpsDetail): Relationship to the owning fps.
    """
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fps_id = Column(
        Integer,
        ForeignKey("fps_details.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    hashed_key = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationship
    fps = relationship("fpsDetail", backref="api_keys")
