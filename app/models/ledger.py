"""
Ledger model module.

Defines the SQLAlchemy model for financial audit logs (debits and credits).
Provides a historical record of all balance changes for fpss.
"""
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.core.database import Base

class LedgerEntry(Base):
    """
    SQLAlchemy model for auditing financial movements (DEBIT/CREDIT) for a fps.

    Provides a historical record of all balance changes, ensuring traceability.

    Attributes:
        id (int): Primary key for the ledger entry.
        fps_id (int): Foreign key linking to the fps.
        amount (Decimal): The amount of the transaction.
        currency (str): The currency of the transaction (default is 'NPR').
        entry_type (str): The type of entry (e.g., 'CREDIT', 'DEBIT').
        description (str): A brief description of the transaction.
        created_at (datetime): Timestamp when the entry was created.
        fps (fpsDetail): Relationship to the associated fps.
    """
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fps_id = Column(Integer, ForeignKey("fps_details.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="NPR")
    entry_type = Column(String(50), nullable=False) # e.g., "CREDIT", "DEBIT"
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    fps = relationship("fpsDetail", back_populates="ledger_entries")
