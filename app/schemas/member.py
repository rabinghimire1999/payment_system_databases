from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal


class MemberCreate(BaseModel):
    fps_name: str
    name: str
    email: EmailStr
    kyc_details: Optional[Dict[str, Any]] = None
    wallet_address: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v):
        return v.lower()


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    kyc_details: Optional[Dict[str, Any]] = None
    wallet_address: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v is None:
            return v
        if v not in ["pending", "active", "suspended"]:
            raise ValueError("Status must be pending, active or suspended")
        return v


class MemberResponse(BaseModel):
    id: int
    fps_id: int
    name: str
    email: str
    kyc_details: Optional[Dict[str, Any]] = None
    wallet_address: Optional[str] = None
    balance: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemberLedgerEntryResponse(BaseModel):
    id: int
    member_id: int
    fps_id: int
    entry_type: str
    amount: Decimal
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MemberBalanceOperation(BaseModel):
    amount: Decimal
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v