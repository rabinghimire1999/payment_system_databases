"""
Ledger schema module.

Defines Pydantic models for Ledger entry validation and serialization.
Used for documenting financial movements and providing audit logs.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer
from decimal import Decimal
from datetime import datetime

class LedgerEntryBase(BaseModel):
    """
    Base properties for a Ledger entry, documenting a financial movement.

    Attributes:
        fps_id (int): ID of the associated fps.
        amount (Decimal): The amount of the movement.
        currency (str): Currency code (default 'NPR').
        entry_type (str): Type of entry (e.g., 'CREDIT', 'DEBIT').
        description (str): Optional description of the entry.
    """
    fps_id: int
    amount: Decimal
    currency: str = "NPR"
    entry_type: str
    description: Optional[str] = None

class LedgerEntryCreate(LedgerEntryBase):
    """
    Properties required to create a new ledger entry.

    Attributes:
        fps_id (int): ID of the associated fps.
        amount (Decimal): The amount of the movement.
        currency (str): Currency code (default 'NPR').
        entry_type (str): Type of entry (e.g., 'CREDIT', 'DEBIT').
        description (str): Optional description of the entry.
    """
    pass

class LedgerEntryResponse(LedgerEntryBase):
    """
    Primary response schema for Ledger entry details.

    Attributes:
        id (int): Unique identifier of the ledger entry.
        created_at (datetime): Timestamp when the entry was created.
    """
    id: int
    created_at: datetime

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
