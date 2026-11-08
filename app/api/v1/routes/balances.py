"""Balance API routes.

This module provides endpoints for retrieving and manually crediting fps 
balances. It delegates business logic to the BalanceService.
"""

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.balance import CreditRequest, BalanceResponse
from app.services.balance import BalanceService

router = APIRouter()

@router.get("/{id}/balance", response_model=BalanceResponse)
def get_balance(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    """Retrieve the current liquid balance of a specific fps.

    Args:
        db: Database session.
        id: fps ID.

    Returns:
        BalanceResponse: The balance details.
    """
    return BalanceService.get_balance(db=db, id=id)

@router.patch("/{id}/credit", response_model=BalanceResponse)
def credit_balance(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    credit_in: CreditRequest
) -> Any:
    """Atomically credit a fps's balance.

    Args:
        db: Database session.
        id: fps ID.
        credit_in: Credit data.

    Returns:
        BalanceResponse: The updated balance details.
    """
    return BalanceService.credit_balance(db=db, id=id, credit_in=credit_in)
