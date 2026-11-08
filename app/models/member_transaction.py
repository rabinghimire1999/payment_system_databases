# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.core.database import Base


class MemberTransaction(Base):
    __tablename__ = "member_transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    receiver_member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String, nullable=False, server_default="NPR")
    status = Column(String, nullable=False, server_default="pending")
    payment_id = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("Member", foreign_keys=[sender_member_id])
    receiver = relationship("Member", foreign_keys=[receiver_member_id])