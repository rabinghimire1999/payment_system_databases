import logging
from fastapi import APIRouter, Depends, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.member_transaction import MemberTransactionCreate, MemberTransactionUpdate
from app.services.member_transaction import (
    create_member_transaction,
    get_member_transaction,
    update_member_transaction,
    get_all_member_transactions
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_member_transaction_route(payload: MemberTransactionCreate, db: Session = Depends(get_db)):
    return create_member_transaction(payload, db)


@router.get("/{transaction_id}", status_code=status.HTTP_200_OK)
def get_member_transaction_route(transaction_id: int, db: Session = Depends(get_db)):
    return get_member_transaction(transaction_id, db)


@router.patch("/{transaction_id}", status_code=status.HTTP_200_OK)
def update_member_transaction_route(transaction_id: int, payload: MemberTransactionUpdate, db: Session = Depends(get_db)):
    return update_member_transaction(transaction_id, payload, db)

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_member_transactions_route(db: Session = Depends(get_db)):
    return get_all_member_transactions(db)