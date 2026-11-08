import enum
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, Text, DateTime, func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.core.database import Base


class TransactionStatus(enum.Enum):
    """
    Enum representing the possible states of a financial transaction.
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Transaction(Base):
    """
    SQLAlchemy model representing a financial transfer between two fpss.

    Tracks sender, receiver, amount, and status throughout the payment lifecycle.

    Attributes:
        id (int): Primary key for the transaction.
        sender_id (int): Foreign key linking to the sender fps.
        receiver_id (int): Foreign key linking to the receiver fps.
        amount (Decimal): The amount transferred.
        currency (str): The currency of the transaction (default is 'NPR').
        status (TransactionStatus): Current status of the transaction.
        rafiki_payment_id (str): Unique payment ID from the Rafiki system.
        created_at (datetime): Timestamp when the transaction was initiated.
        updated_at (datetime): Timestamp of the last status update.
        sender (fpsDetail): Relationship to the sender fps.
        receiver (fpsDetail): Relationship to the receiver fps.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("fps_details.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("fps_details.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="NPR", server_default="NPR")
    status = Column(Enum(TransactionStatus, name="transaction_status_enum"), nullable=False, default=TransactionStatus.PENDING, server_default="PENDING")

    rafiki_payment_id = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    sender = relationship("fpsDetail", foreign_keys=[sender_id], back_populates="sent_transactions")
    receiver = relationship("fpsDetail", foreign_keys=[receiver_id], back_populates="received_transactions")
