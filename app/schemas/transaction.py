"""
Transaction schema module.

Defines Pydantic models for Transaction data validation, creation, and responses.
Includes validation logic for transaction amounts and status updates.
"""
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator, field_serializer, model_validator
from decimal import Decimal
from datetime import datetime
from app.models.transaction import TransactionStatus

class fpsMetadata(BaseModel):
    """
    Schema for minimal fps metadata included in transaction responses.
    """
    id: int
    account_number: str
    fps_name: str
    wallet_address_id: Optional[str] = None
    wallet_address_url: Optional[str] = None

class TransactionBase(BaseModel):
    """
    Base properties for a Transaction, shared across Create and Response schemas.

    Attributes:
        sender_id (int): ID of the sender fps.
        receiver_id (int): ID of the receiver fps.
        amount (Decimal): Transaction amount.
        currency (str): Currency code (default 'NPR').
        status (TransactionStatus): Initial status (default 'PENDING').
        rafiki_payment_id (str): Optional Rafiki payment identifier.
    """
    model_config = ConfigDict(extra='forbid')
    sender_id: int
    receiver_id: int
    amount: Decimal
    currency: Optional[str] = "NPR"
    status: Optional[TransactionStatus] = TransactionStatus.PENDING
    rafiki_payment_id: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """
        Ensures transaction amount is strictly positive.

        Args:
            v (Decimal): The amount to validate.

        Returns:
            Decimal: The validated amount.

        Raises:
            ValueError: If the amount is less than or equal to zero.
        """
        if v < 0:
            raise ValueError('Transaction amount must be greater than or equal to zero')
        return v

class TransactionCreate(TransactionBase):
    """
    Properties required to initialize a new transaction.

    Attributes:
        sender_id (int): ID of the sender fps.
        receiver_id (int): ID of the receiver fps.
        amount (Decimal): Transaction amount.
        currency (str): Currency code (default 'NPR').
        status (TransactionStatus): Initial status (default 'PENDING').
        rafiki_payment_id (str): Optional Rafiki payment identifier.
    """
    pass

class TransactionUpdate(BaseModel):
    """
    Properties that can be updated for an existing transaction.

    Attributes:
        status (TransactionStatus): New status of the transaction.
        rafiki_payment_id (str): Updated Rafiki payment identifier.
    """
    status: Optional[TransactionStatus] = None
    rafiki_payment_id: Optional[str] = None

class TransactionInDBBase(TransactionBase):
    """
    Internal base schema for transactions retrieved from the database.

    Attributes:
        id (int): Unique identifier of the transaction.
        created_at (datetime): Timestamp when initiated.
        updated_at (datetime): Timestamp of last update.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("amount")
    def serialize_amount(self, amount: Decimal) -> str:
        """
        Formats Decimal amount to a standard string with 2 decimal places.

        Args:
            amount (Decimal): The amount to serialize.

        Returns:
            str: The formatted amount string.
        """
        return f"{amount:.2f}"

    model_config = ConfigDict(from_attributes=True)

class Transaction(BaseModel):
    """
    Primary response schema for Transaction details.

    Organized to show sender and receiver metadata first, removing redundant ID fields.
    """
    sender_metadata: Optional[fpsMetadata] = None
    receiver_metadata: Optional[fpsMetadata] = None
    id: int
    amount: Decimal
    currency: str
    status: TransactionStatus
    rafiki_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_metadata(cls, value: Any) -> Any:
        """
        Populates sender and receiver metadata from relationships if available.
        """
        if isinstance(value, dict):
            return value
        
        def get_meta(coop):
            if not coop:
                return None
            rafiki = coop.rafiki_metadata or {}
            return {
                "id": coop.id,
                "account_number": getattr(coop, "account_number", "N/A"),
                "fps_name": coop.fps_name,
                "wallet_address_id": rafiki.get("wallet_address_id"),
                "wallet_address_url": rafiki.get("wallet_address_url")
            }

        return {
            "sender_metadata": get_meta(getattr(value, "sender", None)),
            "receiver_metadata": get_meta(getattr(value, "receiver", None)),
            "id": value.id,
            "amount": value.amount,
            "currency": value.currency,
            "status": value.status,
            "rafiki_payment_id": value.rafiki_payment_id,
            "created_at": value.created_at,
            "updated_at": value.updated_at,
        }

    @field_serializer("amount")
    def serialize_amount(self, amount: Decimal) -> str:
        return f"{amount:.2f}"

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        if value.tzinfo is None:
            return value.isoformat() + "Z"
        return value.isoformat().replace("+00:00", "Z")

    model_config = ConfigDict(from_attributes=True)
