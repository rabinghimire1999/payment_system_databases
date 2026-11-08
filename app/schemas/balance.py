"""
Balance schema module.

Defines Pydantic models for balance-related data validation and serialization.
Includes schemas for credit requests and balance responses.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
from decimal import Decimal
from datetime import datetime

class CreditRequest(BaseModel):
    """
    Schema for manual balance credit requests.

    Attributes:
        amount (Decimal): The amount to be credited.
        currency (str): The currency of the credit (default 'NPR').
        description (str): Description of the credit operation.
    """
    amount: Decimal
    currency: str = "NPR"
    description: str = "Manual Deposit by Admin"

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """
        Ensures credit amount is strictly positive.

        Args:
            v (Decimal): The amount to validate.

        Returns:
            Decimal: The validated amount.

        """
        if v <= 0:
            raise ValueError("Amount must be strictly positive")
        return v


class BalanceBase(BaseModel):
    """
    Base properties for a Balance record.

    Attributes:
        fps_id (int): ID of the fps.
        balance (Decimal): Current balance amount.
        currency (str): Currency code.
    """
    fps_id: int
    balance: Decimal
    currency: str

class BalanceResponse(BalanceBase):
    """
    Primary response schema for Balance details.

    Attributes:
        id (int): Unique identifier of the balance record.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("balance")
    def serialize_balance(self, balance: Decimal) -> str:
        """
        Formats Decimal balance to a standard string with 2 decimal places.

        Args:
            balance (Decimal): The balance amount to serialize.

        Returns:
            str: The formatted balance string.
        """
        return f"{balance:.2f}"

    model_config = ConfigDict(from_attributes=True)