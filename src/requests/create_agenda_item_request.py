from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ItemType(str, Enum):
    EVENT = "Event"
    LOG = "Log"

class TimeSlotRequest(BaseModel):
    startTime: datetime
    endTime: datetime

class CreateAgendaItemRequest(BaseModel):
    summary: str = Field(..., min_length=1, max_length=64)
    description: Optional[str] = Field(None, min_length=1, max_length=512)
    location: Optional[str] = Field(None, min_length=1, max_length=64)
    itemType: ItemType
    timeSlot: TimeSlotRequest