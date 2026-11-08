"""
Balance model module.

Defines the SQLAlchemy model for tracking fps balances.
Each fps is associated with a single balance record.
"""
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.core.database import Base

class Balance(Base):
    """
    SQLAlchemy model for tracking the current liquid balance for a fps.

    Attributes:
        id (int): Primary key for the balance record.
        fps_id (int): Foreign key linking to the fps.
        balance (Decimal): The current financial balance.
        currency (str): The currency of the balance (default is 'NPR').
        created_at (datetime): Timestamp when the balance record was created.
        updated_at (datetime): Timestamp when the balance record was last updated.
        fps (fpsDetail): Relationship to the associated fps.
    """
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fps_id = Column(Integer, ForeignKey("fps_details.id", ondelete="CASCADE"), nullable=False, unique=True)
    balance = Column(Numeric(15, 2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False, default="NPR")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    fps = relationship("fpsDetail", back_populates="balance")
