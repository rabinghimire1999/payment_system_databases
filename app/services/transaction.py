"""Transaction Service module.

Contains business logic for financial transfers, including validation,
atomic balance updates, and ledger auditing.
"""

import logging
from typing import List, Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.fps import fpsDetail as fpsDetail
from app.models.transaction import Transaction, TransactionStatus
from app.models.balance import Balance
from app.models.ledger import LedgerEntry
from app.schemas.transaction import TransactionCreate, TransactionUpdate

logger = logging.getLogger(__name__)

class TransactionService:
    """Service class for Transaction operations."""

    @staticmethod
    def create_transaction(db: Session, transaction_in: TransactionCreate) -> Transaction:
        """Create a new transaction record in PENDING status.

        Args:
            db: Database session.
            transaction_in: Transaction creation data.

        Returns:
            Transaction: The newly created transaction.

        Raises:
            HTTPException: If sender/receiver not found or inactive.
        """
        # 1. Verify Sender
        sender = db.query(fpsDetail).filter(fpsDetail.id == transaction_in.sender_id).first()
        if not sender:
            raise HTTPException(status_code=404, detail=f"Sender ID {transaction_in.sender_id} not found")
        
        # 2. Verify Receiver
        receiver = db.query(fpsDetail).filter(fpsDetail.id == transaction_in.receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail=f"Receiver ID {transaction_in.receiver_id} not found")
        
        # 3. Status Checks
        if sender.calculated_status != "ACTIVE":
            raise HTTPException(status_code=400, detail=f"Sender (ID {sender.id}) is not ACTIVE")
        if receiver.calculated_status != "ACTIVE":
            raise HTTPException(status_code=400, detail=f"Receiver (ID {receiver.id}) is not ACTIVE")
            
        if transaction_in.sender_id == transaction_in.receiver_id:
            raise HTTPException(status_code=400, detail="Sender and Receiver cannot be the same")

        try:
            transaction_data = transaction_in.model_dump()
            transaction_data["status"] = TransactionStatus.PENDING
            
            new_transaction = Transaction(**transaction_data)
            db.add(new_transaction)
            db.commit()
            db.refresh(new_transaction)
            return new_transaction
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise HTTPException(status_code=500, detail="Failed to create transaction")

    @staticmethod
    def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Retrieve all transactions with pagination.

        Args:
            db: Database session.
            skip: Offset.
            limit: Limit.

        Returns:
            List[Transaction]: List of transactions.
        """
        from sqlalchemy.orm import joinedload
        return db.query(Transaction).options(
            joinedload(Transaction.sender),
            joinedload(Transaction.receiver)
        ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_transaction_by_id(db: Session, id: int) -> Optional[Transaction]:
        """Retrieve a transaction by ID.

        Args:
            db: Database session.
            id: Transaction ID.

        Returns:
            Optional[Transaction]: The transaction.
        """
        from sqlalchemy.orm import joinedload
        return db.query(Transaction).options(
            joinedload(Transaction.sender),
            joinedload(Transaction.receiver)
        ).filter(Transaction.id == id).first()

    @staticmethod
    def get_transaction_by_payment_id(db: Session, payment_id: str) -> Optional[Transaction]:
        """Retrieve a transaction by payment ID.

        Args:
            db: Database session.
            payment_id: Rafiki payment ID.

        Returns:
            Optional[Transaction]: The transaction.
        """
        from sqlalchemy.orm import joinedload
        return db.query(Transaction).options(
            joinedload(Transaction.sender),
            joinedload(Transaction.receiver)
        ).filter(Transaction.rafiki_payment_id == payment_id).first()

    @staticmethod
    def get_transactions_by_coop_id(db: Session, coop_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Retrieve all transactions associated with a specific fps ID.

        Args:
            db: Database session.
            coop_id: fps ID.
            skip: Offset.
            limit: Limit.

        Returns:
            List[Transaction]: List of transactions where coop_id is sender or receiver.
        """
        from sqlalchemy import or_
        from sqlalchemy.orm import joinedload
        return db.query(Transaction).options(
            joinedload(Transaction.sender),
            joinedload(Transaction.receiver)
        ).filter(
            or_(Transaction.sender_id == coop_id, Transaction.receiver_id == coop_id)
        ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_transaction_status(db: Session, id: int, transaction_update: TransactionUpdate) -> Transaction:
        """Update transaction status and handle atomic fund movement.

        Args:
            db: Database session.
            id: Transaction ID.
            transaction_update: Update data.

        Returns:
            Transaction: The updated transaction.
        """
        try:
            db_transaction = db.query(Transaction).filter(Transaction.id == id).with_for_update().first()
            if not db_transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")
            
            old_status = db_transaction.status
            new_status = transaction_update.status
            
            if old_status == TransactionStatus.COMPLETED and new_status != TransactionStatus.COMPLETED:
                raise HTTPException(status_code=400, detail="Cannot change status of a completed transaction")

            if new_status == TransactionStatus.COMPLETED and old_status != TransactionStatus.COMPLETED:
                # 1. Row Locking (Consistent order to prevent deadlock)
                first_id = min(db_transaction.sender_id, db_transaction.receiver_id)
                second_id = max(db_transaction.sender_id, db_transaction.receiver_id)
                
                # Fetch and lock in consistent order to prevent deadlock
                locked_balance_1 = db.query(Balance).filter(Balance.fps_id == first_id).with_for_update().first()
                locked_balance_2 = db.query(Balance).filter(Balance.fps_id == second_id).with_for_update().first()
                
                if not locked_balance_1 or not locked_balance_2:
                    raise HTTPException(status_code=400, detail="One or more fps balances not initialized")

                # Map to sender/receiver
                if db_transaction.sender_id == first_id:
                    sender_balance = locked_balance_1
                    receiver_balance = locked_balance_2
                else:
                    sender_balance = locked_balance_2
                    receiver_balance = locked_balance_1
                
                # if sender_balance.balance < db_transaction.amount:
                #     raise HTTPException(status_code=400, detail="Insufficient funds")

                # 2. Update Balances
                sender_balance.balance -= db_transaction.amount
                receiver_balance.balance += db_transaction.amount

                # 3. Ledger Audit
                db.add(LedgerEntry(
                    fps_id=db_transaction.sender_id,
                    amount=db_transaction.amount,
                    currency=db_transaction.currency,
                    entry_type="DEBIT",
                    description=f"Transaction {id}: Payment to Coop ID {db_transaction.receiver_id}"
                ))
                db.add(LedgerEntry(
                    fps_id=db_transaction.receiver_id,
                    amount=db_transaction.amount,
                    currency=db_transaction.currency,
                    entry_type="CREDIT",
                    description=f"Transaction {id}: Payment from Coop ID {db_transaction.sender_id}"
                ))

            # 4. Finalize Update
            update_data = transaction_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_transaction, key, value)
            
            db.commit()
            db.refresh(db_transaction)
            return db_transaction

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating transaction {id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during update")
