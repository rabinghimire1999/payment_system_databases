"""Balance Service module.

Contains business logic for managing fps balances, including
retrieval and atomic credit operations with auditing.
"""

import logging
from typing import Optional, Any
from fastapi import HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from app.models.balance import Balance
from app.models.ledger import LedgerEntry
from app.models.fps import fpsDetail as fpsDetail
from app.schemas.balance import CreditRequest

logger = logging.getLogger(__name__)

class BalanceService:
    """Service class for Balance operations."""

    @staticmethod
    def get_balance(db: Session, id: int) -> Balance:
        """Retrieve the current balance of a fps.

        Args:
            db: Database session.
            id: fps ID.

        Returns:
            Balance: The balance record.

        Raises:
            HTTPException: If fps or balance record is not found.
        """
        coop = db.query(fpsDetail).filter(fpsDetail.id == id).first()
        if not coop:
            raise HTTPException(status_code=404, detail="fps not found")

        balance = db.query(Balance).filter(Balance.fps_id == id).first()
        if not balance:
            raise HTTPException(status_code=404, detail="Balance record not found")
        
        return balance

    @staticmethod
    def credit_balance(db: Session, id: int, credit_in: CreditRequest) -> Balance:
        """Atomically credit a fps balance and record the audit entry.

        Args:
            db: Database session.
            id: fps ID.
            credit_in: Credit data.

        Returns:
            Balance: The updated balance record.
        """
        try:
            # 1. Verify coop
            coop = db.query(fpsDetail).filter(fpsDetail.id == id).first()
            if not coop:
                raise HTTPException(status_code=404, detail="fps not found")

            # 2. Lock balance
            balance = db.query(Balance).filter(Balance.fps_id == id).with_for_update().first()

            if not balance:
                balance = Balance(
                    fps_id=id,
                    balance=Decimal("0.00"),
                    currency=credit_in.currency
                )
                db.add(balance)
                db.flush()

            # 3. Update and Audit
            balance.balance += credit_in.amount
            
            db.add(LedgerEntry(
                fps_id=id,
                amount=credit_in.amount,
                currency=credit_in.currency,
                entry_type="CREDIT",
                description=credit_in.description or f"Manual credit of {credit_in.amount}"
            ))

            db.commit()
            db.refresh(balance)
            return balance

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error crediting balance for coop {id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
