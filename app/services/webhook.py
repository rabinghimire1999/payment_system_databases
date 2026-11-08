"""Webhook Service module.

Contains business logic for processing and retrieving external system events,
including idempotency checks.
"""

import logging
from typing import List, Optional, Any
from fastapi import HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.models.webhook import WebhookEvent
from app.models.status import Status
from app.schemas.webhook import WebhookEventCreate

logger = logging.getLogger(__name__)

class WebhookService:
    """Service class for Webhook operations."""

    @staticmethod
    def create_event(db: Session, payload: WebhookEventCreate) -> WebhookEvent:
        """Receive and record a webhook event with idempotency check.

        Args:
            db: Database session.
            payload: Event data.

        Returns:
            WebhookEvent: The recorded event.

        Raises:
            HTTPException: 400 if event ID exists, 500 on error.
        """
        try:
            # Idempotency check
            existing_event = db.query(WebhookEvent).filter(WebhookEvent.id == payload.id).first()
            if existing_event:
                raise HTTPException(
                    status_code=400,
                    detail=f"Webhook event with id '{payload.id}' already exists"
                )

            # Resolve status (PENDING by default)
            status_record = db.query(Status).filter(Status.name == "PENDING").first()
            if not status_record:
                status_record = Status(name="PENDING")
                db.add(status_record)
                db.flush()

            new_event = WebhookEvent(
                id=payload.id,
                type=payload.type,
                data=payload.data,
                status_id=status_record.id
            )
            db.add(new_event)
            db.commit()
            db.refresh(new_event)
            return new_event
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating webhook event: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    def process_event(db: Session, id: str) -> WebhookEvent:
        """Process a webhook event and update its status.

        Args:
            db: Database session.
            id: Event ID.

        Returns:
            WebhookEvent: The processed event.
        """
        try:
            event = db.query(WebhookEvent).filter(WebhookEvent.id == id).with_for_update().first()
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")

            # Placeholder for actual business logic processing
            # e.g., if event.type == "payment.completed": ...
            
            logger.info(f"Processing webhook event {id} of type {event.type}")
            
            # Transition to PROCESSED
            status_record = db.query(Status).filter(Status.name == "PROCESSED").first()
            if not status_record:
                status_record = Status(name="PROCESSED")
                db.add(status_record)
                db.flush()
            event.status_id = status_record.id
            db.commit()
            db.refresh(event)
            return event

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing webhook event {id}: {e}")
            
            # Re-fetch to update status to FAILED if possible
            event = db.query(WebhookEvent).filter(WebhookEvent.id == id).first()
            if event:
                status_record = db.query(Status).filter(Status.name == "FAILED").first()
                if not status_record:
                    status_record = Status(name="FAILED")
                    db.add(status_record)
                    db.flush()
                event.status_id = status_record.id
                db.commit()
            
            raise HTTPException(status_code=500, detail="Error during webhook processing")

    @staticmethod
    def get_events(
        db: Session, 
        status_param: Optional[str] = None, 
        event_type: Optional[str] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[WebhookEvent]:
        """List webhook events with filters.

        Args:
            db: Database session.
            status_param: Status filter.
            event_type: Type filter.
            skip: Offset.
            limit: Limit.

        Returns:
            List[WebhookEvent]: List of events.
        """
        query = db.query(WebhookEvent)
        if status_param:
            query = query.join(WebhookEvent.status).filter(Status.name == status_param)
        if event_type:
            query = query.filter(WebhookEvent.type == event_type)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_event_by_id(db: Session, id: str) -> Optional[WebhookEvent]:
        """Retrieve a specific webhook event.

        Args:
            db: Database session.
            id: Event ID.

        Returns:
            Optional[WebhookEvent]: The event if found.
        """
        return db.query(WebhookEvent).filter(WebhookEvent.id == id).first()
