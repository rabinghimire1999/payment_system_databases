import logging
from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.member import Member
from app.models.member_ledger_entry import MemberLedgerEntry
from app.models.fps import fpsDetail as fps
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse, MemberLedgerEntryResponse

logger = logging.getLogger(__name__)


def create_member(payload: MemberCreate, db: Session) -> dict:
    try:
        fps = db.query(fps).filter(fps.fps_name == payload.fps_name).first()
        if not fps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"fps with name '{payload.fps_name}' not found"
            )

        member = Member(
            fps_id=fps.id,
            name=payload.name,
            email=payload.email,
            kyc_details=payload.kyc_details,
            wallet_address=payload.wallet_address,
            balance=0
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        logger.info(f"Member created successfully with ID: {member.id}")
        return {
            "status": "success",
            "message": "Member created successfully",
            "data": MemberResponse.model_validate(member)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create member. Possible duplicate email or wallet address."
        )


def get_member(member_id: int, db: Session) -> dict:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )
    logger.info(f"Member fetched successfully: ID {member_id}")
    return {
        "status": "success",
        "data": MemberResponse.model_validate(member)
    }


def get_all_members(db: Session) -> dict:
    members = db.query(Member).order_by(Member.id.asc()).all()
    logger.info(f"All members fetched, count: {len(members)}")
    return {
        "status": "success",
        "total": len(members),
        "data": [MemberResponse.model_validate(m) for m in members]
    }


def get_members_by_fps(fps_id: int, db: Session) -> dict:
    fps = db.query(fps).filter(fps.id == fps_id).first()
    if not fps:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fps with id {fps_id} not found"
        )
    members = db.query(Member).filter(Member.fps_id == fps_id).order_by(Member.id.asc()).all()
    logger.info(f"Members fetched for fps ID: {fps_id}")
    return {
        "status": "success",
        "fps_name": fps.fps_name,
        "total": len(members),
        "data": [MemberResponse.model_validate(m) for m in members]
    }


def update_member(member_id: int, payload: MemberUpdate, db: Session) -> dict:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )

    fields = payload.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update"
        )

    if 'wallet_address' in fields and fields['wallet_address']:
        existing = db.query(Member).filter(
            Member.wallet_address == fields['wallet_address'],
            Member.id != member_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Wallet address {fields['wallet_address']} is already assigned to another member"
            )
        member.status = 'active'

    for key, value in fields.items():
        setattr(member, key, value)

    member.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)
    logger.info(f"Member updated successfully: ID {member_id}")
    return {
        "status": "success",
        "message": "Member updated successfully",
        "data": MemberResponse.model_validate(member)
    }


def credit_member_balance(member_id: int, amount, description: str, db: Session) -> dict:
    member = db.query(Member).filter(Member.id == member_id).with_for_update().first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )

    if not member.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Member with id {member_id} must have a wallet address assigned before any balance operations"
        )

    member.balance += amount
    member.updated_at = datetime.now(timezone.utc)

    ledger_entry = MemberLedgerEntry(
        member_id=member_id,
        fps_id=member.fps_id,
        entry_type="credit",
        amount=amount,
        description=description or f"Credit of {amount} NPR"
    )
    db.add(ledger_entry)
    db.commit()
    db.refresh(member)
    db.refresh(ledger_entry)

    logger.info(f"Member balance credited: ID {member_id}")
    return {
        "status": "success",
        "message": "Member balance credited successfully",
        "data": {
            "member_id": member_id,
            "new_balance": str(member.balance),
            "ledger_entry": MemberLedgerEntryResponse.model_validate(ledger_entry)
        }
    }


# def debit_member_balance(member_id: int, amount, description: str, db: Session) -> dict:
#     member = db.query(Member).filter(Member.id == member_id).with_for_update().first()
#     if not member:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Member with id {member_id} not found"
#         )

#     if not member.wallet_address:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Member with id {member_id} must have a wallet address assigned before any balance operations"
#         )

#     if member.balance < amount:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Insufficient balance. Current balance: {member.balance} NPR"
#         )

#     member.balance -= amount
#     member.updated_at = datetime.now(timezone.utc)

#     ledger_entry = MemberLedgerEntry(
#         member_id=member_id,
#         fps_id=member.fps_id,
#         entry_type="debit",
#         amount=amount,
#         description=description or f"Debit of {amount} NPR"
#     )
#     db.add(ledger_entry)
#     db.commit()
#     db.refresh(member)
#     db.refresh(ledger_entry)

#     logger.info(f"Member balance debited: ID {member_id}")
#     return {
#         "status": "success",
#         "message": "Member balance debited successfully",
#         "data": {
#             "member_id": member_id,
#             "new_balance": str(member.balance),
#             "ledger_entry": MemberLedgerEntryResponse.model_validate(ledger_entry)
#         }
#     }


def get_member_ledger(member_id: int, page: int, page_size: int, db: Session) -> dict:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )

    total = db.query(MemberLedgerEntry).filter(MemberLedgerEntry.member_id == member_id).count()
    entries = db.query(MemberLedgerEntry).filter(
        MemberLedgerEntry.member_id == member_id
    ).order_by(MemberLedgerEntry.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    logger.info(f"Member ledger fetched: ID {member_id}")
    return {
        "status": "success",
        "member_id": member_id,
        "member_name": member.name,
        "page": page,
        "page_size": page_size,
        "total_entries": total,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [MemberLedgerEntryResponse.model_validate(e) for e in entries]
    }