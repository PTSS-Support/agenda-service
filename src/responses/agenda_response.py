from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class ItemType(str, Enum):
    EVENT = "Event"
    LOG = "Log"

class TimeSlot(BaseModel):
    start: datetime
    end: datetime

class AgendaResponse(BaseModel):
    id: str
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    itemType: ItemType
    created: datetime
    updated: datetime
    timeSlot: TimeSlot