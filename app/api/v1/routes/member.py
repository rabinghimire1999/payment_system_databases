import logging
from fastapi import APIRouter, Depends, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.member import MemberCreate, MemberUpdate, MemberBalanceOperation
from app.services.member import (
    create_member,
    get_member,
    get_all_members,
    get_members_by_fps,
    update_member,
    credit_member_balance,
    # debit_member_balance,
    get_member_ledger
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_member_route(payload: MemberCreate, db: Session = Depends(get_db)):
    return create_member(payload, db)


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_members_route(db: Session = Depends(get_db)):
    return get_all_members(db)


@router.get("/{member_id}", status_code=status.HTTP_200_OK)
def get_member_route(member_id: int, db: Session = Depends(get_db)):
    return get_member(member_id, db)


@router.get("/fps/{fps_id}", status_code=status.HTTP_200_OK)
def get_members_by_fps_route(fps_id: int, db: Session = Depends(get_db)):
    return get_members_by_fps(fps_id, db)


@router.patch("/{member_id}", status_code=status.HTTP_200_OK)
def update_member_route(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    return update_member(member_id, payload, db)


@router.patch("/{member_id}/credit", status_code=status.HTTP_200_OK)
def credit_member_route(member_id: int, payload: MemberBalanceOperation, db: Session = Depends(get_db)):
    return credit_member_balance(member_id, payload.amount, payload.description, db)


# @router.patch("/{member_id}/debit", status_code=status.HTTP_200_OK)
# def debit_member_route(member_id: int, payload: MemberBalanceOperation, db: Session = Depends(get_db)):
#     return debit_member_balance(member_id, payload.amount, payload.description, db)


@router.get("/{member_id}/ledger", status_code=status.HTTP_200_OK)
def get_member_ledger_route(member_id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    return get_member_ledger(member_id, page, page_size, db)