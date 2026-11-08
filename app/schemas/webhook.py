"""
Webhook schema module.

Defines Pydantic models for receiving and responding to webhook events.
Used for handling event data from external systems like Rafiki.
"""
from typing import Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.status import StatusSchema

class WebhookEventCreate(BaseModel):
    """
    Schema for receiving new webhook events.

    Attributes:
        id (str): Unique identifier for the event.
        type (str): The type of the webhook event.
        data (dict): The payload of the webhook event.
    """
    id: str
    type: str
    data: Dict[str, Any]

class WebhookEventResponse(BaseModel):
    """
    Schema for webhook event responses.

    Attributes:
        id (str): Unique identifier for the event.
        type (str): The type of the webhook event.
        data (dict): The payload of the webhook event.
        status (str): Current processing status of the event.
        created_at (datetime): Timestamp when the event was received.
    """
    id: str
    type: str
    data: Dict[str, Any]
    status: StatusSchema
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
