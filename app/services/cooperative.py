"""fps Service module.

Contains business logic for managing fpss, including registration,
uniqueness checks, and status lifecycle management.
"""

import logging
from typing import List, Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.fps import (
    fpsDetail,
    fpsType,
    RegistrationAuthority
)
from app.models.status import (
    Status
)
from app.models.balance import Balance
from app.schemas.fps import fpsCreate, fpsUpdate

logger = logging.getLogger(__name__)

class fpsService:
    """Service class for fps operations."""

    @staticmethod
    def create_fps(db: Session, coop_in: fpsCreate) -> fpsDetail:
        """Create a new fps record with PENDING status.

        Args:
            db: Database session.
            coop_in: fps creation schema data.

        Returns:
            fpsDetail: The newly created fps.

        Raises:
            HTTPException: If unique constraints are violated or database errors occur.
        """
        try:
            # 1. Uniqueness Checks
            if db.query(fpsDetail).filter(fpsDetail.account_number == coop_in.account_number).first():
                raise HTTPException(status_code=400, detail=f"Account number '{coop_in.account_number}' already exists")
            
            if coop_in.pan_number and db.query(fpsDetail).filter(fpsDetail.pan_number == coop_in.pan_number).first():
                raise HTTPException(status_code=400, detail=f"PAN number '{coop_in.pan_number}' already exists")
            
            if coop_in.fps_code and db.query(fpsDetail).filter(fpsDetail.fps_code == coop_in.fps_code).first():
                raise HTTPException(status_code=400, detail=f"fps code '{coop_in.fps_code}' already exists")
            
            if coop_in.fps_email and db.query(fpsDetail).filter(fpsDetail.fps_email == coop_in.fps_email).first():
                raise HTTPException(status_code=400, detail=f"fps email '{coop_in.fps_email}' already exists")

            # 2. Create the Record
            # Resolve status (PENDING by default)
            status_record = db.query(Status).filter(Status.name == "PENDING").first()
            if not status_record:
                status_record = Status(name="PENDING")
                db.add(status_record)
                db.flush()

            # Resolve type
            coop_type_name = coop_in.fps_type.value if hasattr(coop_in.fps_type, "value") else coop_in.fps_type
            if not coop_type_name:
                coop_type_name = "SAVING"
            type_record = db.query(fpsType).filter(fpsType.name == coop_type_name).first()
            if not type_record:
                type_record = fpsType(name=coop_type_name)
                db.add(type_record)
                db.flush()

            # Resolve registration authority
            authority_record = None
            if coop_in.registration_authority:
                auth_name = coop_in.registration_authority.strip()
                authority_record = db.query(RegistrationAuthority).filter(RegistrationAuthority.name == auth_name).first()
                if not authority_record:
                    authority_record = RegistrationAuthority(name=auth_name)
                    db.add(authority_record)
                    db.flush()

            coop_data = coop_in.model_dump(exclude_unset=True)
            coop_data.pop("status", None)
            coop_data.pop("fps_type", None)
            coop_data.pop("registration_authority", None)

            new_coop = fpsDetail(
                **coop_data,
                status_id=status_record.id,
                fps_type_id=type_record.id,
                registration_authority_id=authority_record.id if authority_record else None
            )
                
            db.add(new_coop)
            db.flush() 

            # 3. Initialize Balance
            new_balance = Balance(fps_id=new_coop.id)
            db.add(new_balance)
            
            db.commit()
            db.refresh(new_coop)
            logger.info(f"Successfully created fps: {new_coop.fps_name} (ID: {new_coop.id})")
            return new_coop

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating fps: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A database error occurred while creating the fps"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating fps: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during creation"
            )

    @staticmethod
    def get_fpss(db: Session, skip: int = 0, limit: int = 100) -> List[fpsDetail]:
        """Retrieve all fpss with pagination.

        Args:
            db: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List[fpsDetail]: List of fpss.
        """
        return db.query(fpsDetail).order_by(fpsDetail.id).offset(skip).limit(limit).all()

    @staticmethod
    def get_fps_by_id(db: Session, id: int) -> Optional[fpsDetail]:
        """Retrieve a fps by ID.

        Args:
            db: Database session.
            id: The fps ID.

        Returns:
            Optional[fpsDetail]: The fps if found, else None.
        """
        return db.query(fpsDetail).filter(fpsDetail.id == id).first()

    @staticmethod
    def get_fps_by_pan(db: Session, pan: str) -> Optional[fpsDetail]:
        """Retrieve a fps by PAN number.

        Args:
            db: Database session.
            pan: The PAN number.

        Returns:
            Optional[fpsDetail]: The fps if found, else None.
        """
        return db.query(fpsDetail).filter(fpsDetail.pan_number == pan).first()

    @staticmethod
    def get_fps_by_email(db: Session, email: str) -> Optional[fpsDetail]:
        """Retrieve a fps by email address.

        Args:
            db: Database session.
            email: The fps email.

        Returns:
            Optional[fpsDetail]: The fps if found, else None.
        """
        return db.query(fpsDetail).filter(fpsDetail.fps_email == email).first()

    @staticmethod
    def get_fps_by_tenant_id(db: Session, tenant_id: str) -> Optional[fpsDetail]:
        """Retrieve a fps by Rafiki tenant ID.

        Args:
            db: Database session.
            tenant_id: The tenant ID.

        Returns:
            Optional[fpsDetail]: The fps if found, else None.
        """
        return db.query(fpsDetail).filter(
            fpsDetail.rafiki_metadata['tenant_id'].as_string() == tenant_id
        ).first()

    @staticmethod
    def get_fps_by_wallet_id(db: Session, wallet_id: str) -> Optional[fpsDetail]:
        """Retrieve a fps by Rafiki wallet address ID.

        Args:
            db: Database session.
            wallet_id: The wallet address ID.

        Returns:
            Optional[fpsDetail]: The fps if found, else None.
        """
        return db.query(fpsDetail).filter(
            fpsDetail.rafiki_metadata['wallet_address_id'].as_string() == wallet_id
        ).first()


    @staticmethod
    def get_fps_by_name_and_account(db: Session, name: str, account: str) -> Optional[fpsDetail]:
        """Retrieve a fps by name and account number.

        Args:
            db: Database session.
            name: The fps name.
            account: The account number.

        Returns:
            Optional[fpsDetail]: The fps if found, else None.
        """
        return db.query(fpsDetail).filter(
            fpsDetail.fps_name == name,
            fpsDetail.account_number == account
        ).first()

    @staticmethod
    def update_fps(db: Session, id: int, coop_update: fpsUpdate) -> fpsDetail:
        """Update fps details and manage status lifecycle.

        Args:
            db: Database session.
            id: The fps ID.
            coop_update: Update data.

        Returns:
            fpsDetail: The updated fps.

        Raises:
            HTTPException: If not found or unique constraints are violated.
        """
        try:
            db_coop = db.query(fpsDetail).filter(fpsDetail.id == id).with_for_update().first()
            if db_coop is None:
                raise HTTPException(status_code=404, detail=f"fps with ID {id} not found")
            
            update_data = coop_update.model_dump(exclude_unset=True)
            
            # 1. Uniqueness Checks
            if "account_number" in update_data:
                existing = db.query(fpsDetail).filter(
                    fpsDetail.account_number == update_data["account_number"],
                    fpsDetail.id != id
                ).first()
                if existing:
                    raise HTTPException(status_code=400, detail=f"Account number '{update_data['account_number']}' already exists")
            
            if "fps_code" in update_data and update_data["fps_code"]:
                existing = db.query(fpsDetail).filter(
                    fpsDetail.fps_code == update_data["fps_code"],
                    fpsDetail.id != id
                ).first()
                if existing:
                    raise HTTPException(status_code=400, detail=f"fps code '{update_data['fps_code']}' already exists")
            
            if "pan_number" in update_data and update_data["pan_number"]:
                existing = db.query(fpsDetail).filter(
                    fpsDetail.pan_number == update_data["pan_number"],
                    fpsDetail.id != id
                ).first()
                if existing:
                    raise HTTPException(status_code=400, detail=f"PAN number '{update_data['pan_number']}' already exists")
                    
            if "fps_email" in update_data and update_data["fps_email"]:
                existing = db.query(fpsDetail).filter(
                    fpsDetail.fps_email == update_data["fps_email"],
                    fpsDetail.id != id
                ).first()
                if existing:
                    raise HTTPException(status_code=400, detail=f"fps email '{update_data['fps_email']}' already exists")
        
            # 2. Apply Updates
            for key, value in update_data.items():
                if key == "rafiki_metadata" and value is not None:
                    explicit_metadata = coop_update.rafiki_metadata.model_dump(exclude_unset=True) if coop_update.rafiki_metadata else {}
                    current_metadata = dict(db_coop.rafiki_metadata or {})
                    for m_key, m_value in explicit_metadata.items():
                        current_metadata[m_key] = m_value
                    db_coop.rafiki_metadata = current_metadata
                elif key == "status":
                    status_name = value.value if hasattr(value, "value") else value
                    status_rec = db.query(Status).filter(Status.name == status_name).first()
                    if not status_rec:
                        status_rec = Status(name=status_name)
                        db.add(status_rec)
                        db.flush()
                    db_coop.status_id = status_rec.id
                elif key == "fps_type":
                    type_name = value.value if hasattr(value, "value") else value
                    type_rec = db.query(fpsType).filter(fpsType.name == type_name).first()
                    if not type_rec:
                        type_rec = fpsType(name=type_name)
                        db.add(type_rec)
                        db.flush()
                    db_coop.fps_type_id = type_rec.id
                elif key == "registration_authority":
                    if value:
                        auth_name = value.strip()
                        auth_rec = db.query(RegistrationAuthority).filter(RegistrationAuthority.name == auth_name).first()
                        if not auth_rec:
                            auth_rec = RegistrationAuthority(name=auth_name)
                            db.add(auth_rec)
                            db.flush()
                        db_coop.registration_authority_id = auth_rec.id
                    else:
                        db_coop.registration_authority_id = None
                else:
                    setattr(db_coop, key, value)
            
            # 3. Status Transition Logic
            m = db_coop.rafiki_metadata or {}
            required_fields = ["tenant_id", "wallet_address_id", "wallet_address_url", "asset_id"]
            is_fully_configured = all(m.get(field) and str(m.get(field)).strip() != "" for field in required_fields)
            
            # If status was explicitly updated in the request, we respect that.
            # Otherwise, we apply automatic transition logic.
            if "status" not in update_data:
                current_status_name = db_coop.status.name if db_coop.status else "PENDING"
                if is_fully_configured:
                    # Auto-promote to ACTIVE only if it wasn't manually INACTIVE
                    if current_status_name in ["PENDING", "FAILED"]:
                        status_record = db.query(Status).filter(Status.name == "ACTIVE").first()
                        if not status_record:
                            status_record = Status(name="ACTIVE")
                            db.add(status_record)
                            db.flush()
                        db_coop.status_id = status_record.id
                else:
                    # If required metadata is missing, it should be PENDING or FAILED
                    if current_status_name == "ACTIVE":
                        status_record = db.query(Status).filter(Status.name == "FAILED").first()
                        if not status_record:
                            status_record = Status(name="FAILED")
                            db.add(status_record)
                            db.flush()
                        db_coop.status_id = status_record.id
            
            db.commit()
            db.refresh(db_coop)
            logger.info(f"Successfully updated fps ID {id}. Status: {db_coop.status.name}")
            return db_coop

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating fps {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not update fps with ID {id} due to a database error"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error updating fps {id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during update"
            )
