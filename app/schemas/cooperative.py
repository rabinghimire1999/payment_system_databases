"""
fps schema module.

Defines Pydantic models for fps data validation, creation, updates, and responses.
Includes complex validation logic for registration details and integration metadata.
"""
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, field_serializer, model_validator
from datetime import date, datetime


# pyrefly: ignore [missing-import]
from email_validator import validate_email, EmailNotValidError
from app.schemas.status import StatusSchema
from app.schemas.fps_type import fpsTypeSchema
from app.schemas.registration_authority import RegistrationAuthoritySchema

class RafikiMetadata(BaseModel):
    """
    Schema for the nested Rafiki integration metadata.

    Attributes:
        tenant_id (str): Unique tenant identifier in Rafiki.
        tenants_secret (str): Secret for tenant authentication.
        wallet_address_id (str): ID of the wallet address in Rafiki.
        wallet_address_url (str): Public URL of the wallet address.
        asset_id (str): ID of the asset used in Rafiki.
        asset_code (str): Human-readable code for the asset (e.g., 'NPR').
        asset_scale (int): Fractional scale for the asset.
    """
    tenant_id: Optional[str] = None
    tenants_secret: Optional[str] = None
    wallet_address_id: Optional[str] = None
    wallet_address_url: Optional[str] = None
    asset_id: Optional[str] = None
    asset_code: Optional[str] = None
    asset_scale: Optional[int] = None
    wallet_address_prefix: Optional[str] = None

class fpsBase(BaseModel):
    """
    Base properties for a fps, shared across Create, Update, and Response schemas.

    Attributes:
        fps_name (str): The name of the fps.
        account_number (str): Unique account number.
        pan_number (str): Unique 9-digit PAN number.
        registration_authority (str): The authority where registered.
        registration_date (date): Date of registration.
        fps_type (str): Type of the fps.
        fps_code (str): Internal identifier code.
        fps_email (EmailStr): Contact email.
        password_hash (str): Hashed password for authentication.
        rafiki_metadata (RafikiMetadata): Integration metadata.
    """
    model_config = ConfigDict(extra='forbid')
    fps_name: Optional[str] = None
    account_number: Optional[str] = None
    pan_number: Optional[str] = None
    registration_authority: Optional[str] = None
    registration_date: Optional[date] = None
    fps_type: Optional[str] = "SAVING"
    fps_code: Optional[str] = None
    fps_email: Optional[EmailStr] = None 
    password_hash: Optional[str] = None
    rafiki_metadata: Optional[RafikiMetadata] = None

    @field_validator('fps_email')
    @classmethod
    def validate_email_strict(cls, v):
        """
        Performs strict email format validation without DNS checks.

        Args:
            v (EmailStr): The email to validate.

        Returns:
            EmailStr: The validated email.

        Raises:
            ValueError: If the email format is invalid.
        """
        if v is not None:
            try:
                # check_deliverability=False avoids DNS record checks which fail for non-real domains
                validate_email(v, check_deliverability=False)
            except EmailNotValidError as e:
                raise ValueError(f"Strict Email Validation Error: {str(e)}")
        return v

    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
        """
        Ensures account number is uppercase and alphanumeric.

        Args:
            v (str): The account number to validate.

        Returns:
            str: The validated account number.

        Raises:
            ValueError: If the number is not alphanumeric or not in full capitals.
        """
        if v is not None:
            if not v.isalnum():
                raise ValueError('Account number must be alphanumeric (no special characters)')
            if any(c.islower() for c in v):
                raise ValueError('Account number must be in full capitals')
        return v

    @field_validator('pan_number')
    @classmethod
    def validate_pan_number(cls, v):
        """
        Ensures PAN number is exactly 9 digits.

        Args:
            v (str): The PAN number to validate.

        Returns:
            str: The validated PAN number.

        Raises:
            ValueError: If the number is not exactly 9 digits or contains non-digits.
        """
        if v is not None:
            if len(v) != 9:
                raise ValueError('PAN number must be exactly 9 characters')
            if not v.isdigit():
                raise ValueError('PAN number must contain only numbers')
        return v

class fpsCreate(fpsBase):
    """
    Properties required to create a new fps.

    Attributes:
        fps_name (str): Name is required.
        account_number (str): Account number is required.
    """
    fps_name: str
    account_number: str

class fpsUpdate(fpsBase):
    """
    Properties that can be optionally updated for an existing fps.

    Attributes:
        status (str): Update the operational status.
    """
    status: Optional[str] = None

class fps(BaseModel):
    """
    Primary response schema for fps details.

    Includes all fields from the database and supports dynamic status calculation.

    Attributes:
        id (int): Database ID.
        fps_name (str): Name.
        account_number (str): Account number.
        pan_number (str): PAN number.
        registration_authority (RegistrationAuthoritySchema): Registration authority schema.
        registration_date (date): Registration date.
        fps_type (fpsTypeSchema): fps type schema.
        fps_code (str): fps code.
        fps_email (str): fps email.
        password_hash (str): Hashed password.
        status (StatusSchema): Calculated status schema.
        rafiki_metadata (RafikiMetadata): Integration metadata.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Update timestamp.
    """
    id: int
    fps_name: str
    account_number: str
    pan_number: Optional[str] = None
    registration_authority: Optional[RegistrationAuthoritySchema] = None
    registration_date: Optional[date] = None
    fps_type: fpsTypeSchema
    fps_code: Optional[str] = None
    fps_email: Optional[str] = None
    password_hash: Optional[str] = None
    status: StatusSchema
    rafiki_metadata: Optional[RafikiMetadata] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_status(cls, value: Any) -> Any:
        """
        Populates status field from calculated_status if available.

        Also handles mapping model attributes to schema fields when initialized
        from an ORM object.

        Args:
            value (Any): The input data (dict or ORM object).

        Returns:
            Any: The processed data dictionary.
        """
        if isinstance(value, dict):
            return value

        # Resolve status, fps_type, and registration_authority objects for serialization
        status_obj = getattr(value, "status", None)
        status_data = None
        if status_obj:
            status_data = {
                "id": getattr(status_obj, "id"),
                "name": getattr(value, "calculated_status", getattr(status_obj, "name")),
                "description": getattr(status_obj, "description", None)
            }

        coop_type_obj = getattr(value, "fps_type", None)
        coop_type_data = None
        if coop_type_obj:
            coop_type_data = {
                "id": getattr(coop_type_obj, "id"),
                "name": getattr(coop_type_obj, "name"),
                "description": getattr(coop_type_obj, "description", None)
            }

        reg_auth_obj = getattr(value, "registration_authority", None)
        reg_auth_data = None
        if reg_auth_obj:
            reg_auth_data = {
                "id": getattr(reg_auth_obj, "id"),
                "name": getattr(reg_auth_obj, "name"),
                "description": getattr(reg_auth_obj, "description", None)
            }

        return {
            "id": getattr(value, "id"),
            "fps_name": getattr(value, "fps_name", getattr(value, "name", None)),
            "account_number": getattr(value, "account_number"),
            "pan_number": getattr(value, "pan_number"),
            "registration_authority": reg_auth_data,
            "registration_date": getattr(value, "registration_date"),
            "fps_type": coop_type_data,
            "fps_code": getattr(value, "fps_code"),
            "fps_email": getattr(value, "fps_email", getattr(value, "email", None)),
            "password_hash": getattr(value, "password_hash", None),
            "status": status_data,
            "created_at": getattr(value, "created_at"),
            "updated_at": getattr(value, "updated_at"),
            "rafiki_metadata": getattr(value, "rafiki_metadata"),
        }


    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        """
        Standardizes ISO8601 timestamps with Z suffix for UTC.

        Args:
            value (datetime): The datetime object to serialize.

        Returns:
            str: The ISO8601 formatted string with 'Z'.
        """
        if value.tzinfo is None:
            return value.isoformat() + "Z"
        return value.isoformat().replace("+00:00", "Z")

    model_config = ConfigDict(from_attributes=True)
