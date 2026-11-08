# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.dialects.postgresql import JSONB
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.core.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    fps_id = Column(Integer, ForeignKey("fps_details.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    kyc_details = Column(JSONB, nullable=True)
    wallet_address = Column(String, nullable=True, unique=True)
    balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    status = Column(String, nullable=False, server_default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    fps = relationship("fpsDetail", foreign_keys=[fps_id])