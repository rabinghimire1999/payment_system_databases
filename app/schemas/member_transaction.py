from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal


class MemberTransactionCreate(BaseModel):
    sender_member_id: int
    receiver_member_id: int
    amount: Decimal
    payment_id: str

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Amount must be greater than or equal to zero")
        return v

    @field_validator("payment_id")
    @classmethod
    def payment_id_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Payment ID cannot be empty")
        return v.strip()


class MemberTransactionUpdate(BaseModel):
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v is None:
            return v
        if v not in ["pending", "completed", "failed"]:
            raise ValueError("Status must be pending, completed or failed")
        return v


class MemberTransactionResponse(BaseModel):
    id: int
    sender_member_id: int
    sender_member_name: Optional[str] = None
    receiver_member_id: int
    receiver_member_name: Optional[str] = None
    amount: Decimal
    currency: str
    status: str
    payment_id: str
    created_at: datetime

    class Config:
        from_attributes = True