"""
Webhook model module.

Defines the SQLAlchemy model for storing incoming webhook events from external systems.
Used for idempotency checks and event auditing.
"""
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, String, JSON, DateTime, Integer, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.status import Status


class WebhookEvent(Base):
    """
    SQLAlchemy model for storing incoming webhook events.

    Provides a record of events received from external systems (e.g., Rafiki),
    allowing for auditing and ensuring that events are processed exactly once.

    Attributes:
        id (str): Primary key, typically a unique identifier from the source system.
        type (str): The type of the webhook event (e.g., 'payment.created').
        data (dict): The full JSON payload of the event.
        status (Status): Current processing status.
        created_at (datetime): Timestamp when the event was received.
    """
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    status = relationship("Status")
