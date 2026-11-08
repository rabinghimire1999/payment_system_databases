# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.core.database import Base


class MemberLedgerEntry(Base):
    __tablename__ = "member_ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    fps_id = Column(Integer, ForeignKey("fps_details.id"), nullable=False)
    entry_type = Column(String, nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    member = relationship("Member", foreign_keys=[member_id])
    fps = relationship("fpsDetail", foreign_keys=[fps_id])