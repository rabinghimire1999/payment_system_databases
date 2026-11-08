"""
fps model module.

Defines the structure for fps organizations, including their types,
status, and integration metadata for the Rafiki system.
"""
# pyrefly: ignore [missing-import]
import enum
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Date, DateTime, func, JSON, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.hybrid import hybrid_property
# pyrefly: ignore [missing-import]
from app.core.database import Base


from app.models.status import Status
from app.models.fps_type import fpsType
from app.models.registration_authority import RegistrationAuthority


class fpsDetail(Base):
    """
    Core model representing a fps organization in the system.

    Stores registration details, contact information, and Rafiki integration metadata.

    Attributes:
        id (int): Primary key for the fps.
        fps_name (str): The name of the fps.
        account_number (str): Unique account number.
        pan_number (str): Unique 9-digit PAN number.
        registration_authority (RegistrationAuthority): The authority where the fps is registered.
        registration_date (date): The date of registration.
        fps_type (fpsType): The type of the fps.
        fps_code (str): Unique internal code for the fps.
        fps_email (str): Unique contact email.
        password_hash (str): Hashed password for authentication.
        status (Status): Current operational status.
        rafiki_metadata (dict): Metadata for Rafiki integration.
        created_at (datetime): Timestamp of record creation.
        updated_at (datetime): Timestamp of last record update.
        balance (Balance): Relationship to the fps's balance record.
        ledger_entries (list[LedgerEntry]): Relationship to the fps's ledger entries.
        sent_transactions (list[Transaction]): Transactions where this fps is the sender.
        received_transactions (list[Transaction]): Transactions where this fps is the receiver.
    """
    __tablename__ = 'fps_details'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fps_name = Column("fps_name", String(255), nullable=False)
    account_number = Column(String(100), unique=True, nullable=False, index=True)
    pan_number = Column(String(9), unique=True, index=True)  # Exactly 9 characters
    registration_date = Column(Date)
    fps_code = Column(String(50), unique=True, index=True)
    fps_email = Column("fps_email", String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=True)
    rafiki_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Foreign Keys to the new tables
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False, index=True)
    fps_type_id = Column(Integer, ForeignKey('fps_types.id'), nullable=False, index=True)
    registration_authority_id = Column(Integer, ForeignKey('registration_authorities.id'), nullable=True, index=True)

    # Relationships to the new tables
    status = relationship("Status")
    fps_type = relationship("fpsType")
    registration_authority = relationship("RegistrationAuthority")

    @hybrid_property
    def calculated_status(self) -> str:
        """
        Dynamically determine if a fps is ACTIVE.

        Requires non-empty tenant_id, wallet_address_id, wallet_address_url, and asset_id
        within the rafiki_metadata.

        Returns:
            str: "ACTIVE" if all required Rafiki fields are present, otherwise returns the stored status name.
        """
        if self.status.name == "INACTIVE":
            return "INACTIVE"
            
        if self.rafiki_metadata and isinstance(self.rafiki_metadata, dict):
            m = self.rafiki_metadata
            required_fields = ["tenant_id", "wallet_address_id", "wallet_address_url", "asset_id"]
            
            # Check if all required fields exist and are not empty strings/None
            is_active = all(m.get(field) and str(m.get(field)).strip() != "" for field in required_fields)
            
            if is_active:
                return "ACTIVE"
                
        return self.status.name if self.status else "PENDING"

    # Relationships
    balance = relationship("Balance", uselist=False, back_populates="fps", cascade="all, delete-orphan")
    ledger_entries = relationship("LedgerEntry", back_populates="fps", cascade="all, delete-orphan")
    
    # Transactions where this coop is the sender
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.sender_id", back_populates="sender")
    # Transactions where this coop is the receiver
    received_transactions = relationship("Transaction", foreign_keys="Transaction.receiver_id", back_populates="receiver")
