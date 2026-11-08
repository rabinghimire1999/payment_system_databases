"""Webhook API routes.

This module provides endpoints for receiving and retrieving external system events.
It delegates business logic to the WebhookService.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.webhook import WebhookEventCreate, WebhookEventResponse
from app.services.webhook import WebhookService

router = APIRouter()

@router.post("/", response_model=WebhookEventResponse, status_code=status.HTTP_201_CREATED)
def create_webhook_event(
    payload: WebhookEventCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    """Receive, record, and process a webhook event.

    Args:
        payload: Event data.
        db: Database session.

    Returns:
        WebhookEventResponse: The processed event.
    """
    event = WebhookService.create_event(db=db, payload=payload)
    return WebhookService.process_event(db=db, id=event.id)

@router.get("/", response_model=List[WebhookEventResponse], status_code=status.HTTP_200_OK)
def get_webhook_events(
    status_param: Optional[str] = None,
    event_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
) -> Any:
    """List recorded webhook events.

    Args:
        status_param: Status filter.
        event_type: Event type filter.
        skip: Offset.
        limit: Limit.
        db: Database session.

    Returns:
        List[WebhookEventResponse]: List of events.
    """
    return WebhookService.get_events(
        db=db, status_param=status_param, event_type=event_type, skip=skip, limit=limit
    )

@router.get("/{id}", response_model=WebhookEventResponse, status_code=status.HTTP_200_OK)
def get_webhook_event(
    id: str,
    db: Session = Depends(deps.get_db)
) -> Any:
    """Retrieve a specific webhook event by ID.

    Args:
        id: Event ID.
        db: Database session.

    Returns:
        WebhookEventResponse: The event details.

    Raises:
        HTTPException: 404 if not found.
    """
    db_event = WebhookService.get_event_by_id(db=db, id=id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Webhook event not found")
    return db_event
