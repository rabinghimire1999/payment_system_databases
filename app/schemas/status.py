from typing import Optional
from pydantic import BaseModel, ConfigDict

class StatusSchema(BaseModel):
    """Schema for fps status table."""
    id: int
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
