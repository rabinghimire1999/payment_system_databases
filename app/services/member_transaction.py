import logging
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import text
from fastapi import HTTPException, status
from app.models.member_transaction import MemberTransaction
from app.models.member import Member
from app.models.member_ledger_entry import MemberLedgerEntry
from app.schemas.member_transaction import MemberTransactionCreate, MemberTransactionUpdate, MemberTransactionResponse
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _get_fps_status(db: Session, fps_id: int) -> str:
    result = db.execute(
        text("SELECT status FROM fps_details WHERE id = :id"),
        {"id": fps_id}
    ).fetchone()
    return result.status if result else None


def create_member_transaction(payload: MemberTransactionCreate, db: Session) -> dict:
    try:
        if payload.sender_member_id == payload.receiver_member_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sender and receiver cannot be the same member"
            )

        sender = db.query(Member).filter(Member.id == payload.sender_member_id).first()
        if not sender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sender member with id {payload.sender_member_id} not found"
            )

        receiver = db.query(Member).filter(Member.id == payload.receiver_member_id).first()
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Receiver member with id {payload.receiver_member_id} not found"
            )

        if _get_fps_status(db, sender.fps_id) != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sender's fps is not active"
            )

        if _get_fps_status(db, receiver.fps_id) != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receiver's fps is not active"
            )

        if sender.status != "active" or receiver.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both members must be active to process a transaction"
            )

        if not sender.wallet_address or not receiver.wallet_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both members must have wallet addresses assigned"
            )


        transaction = MemberTransaction(
            sender_member_id=payload.sender_member_id,
            receiver_member_id=payload.receiver_member_id,
            amount=payload.amount,
            payment_id=payload.payment_id
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        logger.info(f"Member transaction created: ID {transaction.id}")
        return {
            "status": "success",
            "message": "Member transaction created successfully",
            "data": {
                **MemberTransactionResponse.model_validate(transaction).model_dump(mode='json'),
                "sender_member_name": sender.name,
                "receiver_member_name": receiver.name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating member transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create member transaction."
        )


def get_member_transaction(transaction_id: int, db: Session) -> dict:
    transaction = db.query(MemberTransaction).filter(MemberTransaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )
    return {
        "status": "success",
        "data": {
            **MemberTransactionResponse.model_validate(transaction).model_dump(mode='json'),
            "sender_member_name": transaction.sender.name,
            "receiver_member_name": transaction.receiver.name
        }
    }


def update_member_transaction(transaction_id: int, payload: MemberTransactionUpdate, db: Session) -> dict:
    transaction = db.query(MemberTransaction).filter(MemberTransaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )

    fields = payload.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update"
        )

    if transaction.status == 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is already completed"
        )

    if transaction.status == 'failed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a failed transaction"
        )

    if fields.get('status') == 'completed':
        sender = db.query(Member).filter(Member.id == transaction.sender_member_id).with_for_update().first()
        receiver = db.query(Member).filter(Member.id == transaction.receiver_member_id).with_for_update().first()


        sender.balance -= transaction.amount
        sender.updated_at = datetime.now(timezone.utc)
        receiver.balance += transaction.amount
        receiver.updated_at = datetime.now(timezone.utc)

        db.add(MemberLedgerEntry(
            member_id=transaction.sender_member_id,
            fps_id=sender.fps_id,
            entry_type="debit",
            amount=transaction.amount,
            description=f"Transfer to {receiver.name} - payment {transaction.payment_id}"
        ))
        db.add(MemberLedgerEntry(
            member_id=transaction.receiver_member_id,
            fps_id=receiver.fps_id,
            entry_type="credit",
            amount=transaction.amount,
            description=f"Transfer from {sender.name} - payment {transaction.payment_id}"
        ))

    for key, value in fields.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    logger.info(f"Member transaction updated: ID {transaction_id}")
    return {
        "status": "success",
        "message": "Member transaction updated successfully",
        "data": {
            **MemberTransactionResponse.model_validate(transaction).model_dump(mode='json'),
            "sender_member_name": transaction.sender.name,
            "receiver_member_name": transaction.receiver.name
        }
    }

def get_all_member_transactions(db: Session) -> dict:
    transactions = db.query(MemberTransaction).order_by(MemberTransaction.id.asc()).all()
    logger.info(f"All member transactions fetched, count: {len(transactions)}")
    return {
        "status": "success",
        "total": len(transactions),
        "data": [
            {
                **MemberTransactionResponse.model_validate(t).model_dump(mode='json'),
                "sender_member_name": t.sender.name,
                "receiver_member_name": t.receiver.name
            }
            for t in transactions
        ]
    }