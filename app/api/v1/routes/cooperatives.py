"""fps API routes.

This module provides endpoints for managing fps registration, details,
and Rafiki metadata. It delegates business logic to the fpsService.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.fps import fps, fpsCreate, fpsUpdate
from app.services.fps import fpsService

router = APIRouter()

@router.post("/", response_model=fps, status_code=status.HTTP_201_CREATED)
def create_fps(
    *,
    db: Session = Depends(deps.get_db),
    coop_in: fpsCreate
) -> Any:
    """Create a new fps record.

    Args:
        db: Database session.
        coop_in: fps creation schema.

    Returns:
        fps: The created fps.
    """
    return fpsService.create_fps(db=db, coop_in=coop_in)

@router.get("/", response_model=List[fps])
def read_fpss(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Retrieve all fpss.

    Args:
        db: Database session.
        skip: Offset for pagination.
        limit: Max records to return.

    Returns:
        List[fps]: Paginated list of fpss.
    """
    return fpsService.get_fpss(db=db, skip=skip, limit=limit)

@router.get("/pan/{pan}", response_model=fps)
def read_fps_by_pan(
    *,
    db: Session = Depends(deps.get_db),
    pan: str
) -> Any:
    """Retrieve a fps by PAN.

    Args:
        db: Database session.
        pan: 9-digit PAN number.

    Returns:
        fps: The fps if found.

    Raises:
        HTTPException: 400 if invalid format, 404 if not found.
    """
    if not (pan.isdigit() and len(pan) == 9):
        raise HTTPException(status_code=400, detail="Invalid PAN format. Must be 9 digits.")
    
    db_coop = fpsService.get_fps_by_pan(db=db, pan=pan)
    if not db_coop:
        raise HTTPException(status_code=404, detail="fps not found")
    return db_coop

@router.get("/lookup", response_model=fps)
def read_fps_by_name_and_account(
    *,
    db: Session = Depends(deps.get_db),
    fps_name: str,
    account_number: str
) -> Any:
    """Retrieve a fps by name and account number.

    Args:
        db: Database session.
        fps_name: Name of the fps.
        account_number: Account number.

    Returns:
        fps: The fps if found.

    Raises:
        HTTPException: 404 if not found.
    """
    db_coop = fpsService.get_fps_by_name_and_account(
        db=db, name=fps_name, account=account_number
    )
    if not db_coop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="fps not found with the provided name and account number"
        )
    return db_coop

@router.get("/{id:int}", response_model=fps)
def read_fps_by_id(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    """Retrieve a fps by database ID.

    Args:
        db: Database session.
        id: fps primary key.

    Returns:
        fps: The fps if found.

    Raises:
        HTTPException: 404 if not found.
    """
    db_coop = fpsService.get_fps_by_id(db=db, id=id)
    if not db_coop:
        raise HTTPException(status_code=404, detail="fps not found")
    return db_coop

@router.get("/wallet/{wallet_id}", response_model=fps)
def read_fps_by_wallet_id(
    *,
    db: Session = Depends(deps.get_db),
    wallet_id: str
) -> Any:
    """Retrieve a fps by Rafiki wallet address ID.

    Args:
        db: Database session.
        wallet_id: Rafiki wallet address ID.

    Returns:
        fps: The fps if found.

    Raises:
        HTTPException: 404 if not found.
    """
    db_coop = fpsService.get_fps_by_wallet_id(db=db, wallet_id=wallet_id)
    if not db_coop:
        raise HTTPException(status_code=404, detail="fps not found")
    return db_coop

@router.get("/{tenant_id}", response_model=fps)
def read_fps_by_tenant_id(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: str
) -> Any:
    """Retrieve a fps by Rafiki tenant ID.

    Args:
        db: Database session.
        tenant_id: Rafiki tenant ID.

    Returns:
        fps: The fps if found.

    Raises:
        HTTPException: 404 if not found.
    """
    db_coop = fpsService.get_fps_by_tenant_id(db=db, tenant_id=tenant_id)
    if not db_coop:
        raise HTTPException(status_code=404, detail="fps not found")
    return db_coop

@router.get("/email/{email}", response_model=fps)
def read_fps_by_email(
    *,
    db: Session = Depends(deps.get_db),
    email: str
) -> Any:
    """Retrieve a fps by email address.

    Args:
        db: Database session.
        email: fps email address.

    Returns:
        fps: The fps if found.

    Raises:
        HTTPException: 404 if not found.
    """
    db_coop = fpsService.get_fps_by_email(db=db, email=email)
    if not db_coop:
        raise HTTPException(status_code=404, detail="fps not found")
    return db_coop

@router.patch("/{id}", response_model=fps)
def update_fps(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    coop_update: fpsUpdate
) -> Any:
    """Update fps details.

    Args:
        db: Database session.
        id: fps ID.
        coop_update: Update data.

    Returns:
        fps: The updated fps.
    """
    return fpsService.update_fps(db=db, id=id, coop_update=coop_update)
