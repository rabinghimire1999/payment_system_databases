"""Transaction API routes.

This module provides endpoints for creating, listing, and updating the status 
of financial transfers between fpss. It delegates business logic to 
the TransactionService.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.transaction import Transaction as TransactionSchema, TransactionCreate, TransactionUpdate
from app.services.transaction import TransactionService

router = APIRouter()

@router.get("/", response_model=List[TransactionSchema])
def read_transactions(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Retrieve all transactions.

    Args:
        db: Database session.
        skip: Offset.
        limit: Limit.

    Returns:
        List[Transaction]: Paginated transactions.
    """
    return TransactionService.get_transactions(db=db, skip=skip, limit=limit)

@router.post("/", response_model=TransactionSchema, status_code=status.HTTP_201_CREATED)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: TransactionCreate
) -> Any:
    """Create a new transaction record.

    Args:
        db: Database session.
        transaction_in: Creation data.

    Returns:
        Transaction: The created transaction.
    """
    return TransactionService.create_transaction(db=db, transaction_in=transaction_in)

@router.get("/{id}", response_model=TransactionSchema)
def read_transaction(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    """Retrieve a specific transaction by ID.

    Args:
        db: Database session.
        id: Transaction ID.

    Returns:
        Transaction: The transaction.

    Raises:
        HTTPException: 404 if not found.
    """
    db_transaction = TransactionService.get_transaction_by_id(db=db, id=id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.get("/payment/{payment_id}", response_model=TransactionSchema)
def read_transaction_by_payment_id(
    *,
    db: Session = Depends(deps.get_db),
    payment_id: str
) -> Any:
    """Retrieve a specific transaction by payment ID.

    Args:
        db: Database session.
        payment_id: Payment ID.

    Returns:
        Transaction: The transaction.

    Raises:
        HTTPException: 404 if not found.
    """
    db_transaction = TransactionService.get_transaction_by_payment_id(db=db, payment_id=payment_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.get("/fps/{coop_id}", response_model=List[TransactionSchema])
def read_transactions_by_coop_id(
    *,
    db: Session = Depends(deps.get_db),
    coop_id: int,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Retrieve all transactions for a specific fps.

    Args:
        db: Database session.
        coop_id: fps ID.
        skip: Offset.
        limit: Limit.

    Returns:
        List[Transaction]: List of transactions.
    """
    return TransactionService.get_transactions_by_coop_id(db=db, coop_id=coop_id, skip=skip, limit=limit)

@router.patch("/{id}", response_model=TransactionSchema)
def update_transaction_status(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    transaction_update: TransactionUpdate
) -> Any:
    """Update the status of a transaction.

    Args:
        db: Database session.
        id: Transaction ID.
        transaction_update: Update data.

    Returns:
        Transaction: The updated transaction.
    """
    return TransactionService.update_transaction_status(db=db, id=id, transaction_update=transaction_update)
