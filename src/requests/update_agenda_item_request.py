from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from src.constants.validation_contraints import MAX_LENGTH_LOCATION, MAX_LENGTH_DESCRIPTION, MAX_LENGTH_SUMMARY, MIN_LENGTH
from src.enums.item_type import ItemType

class TimeSlotRequest(BaseModel):
    startTime: datetime
    endTime: datetime

class UpdateAgendaItemRequest(BaseModel):
    summary: str = Field(..., min_length=MIN_LENGTH, max_length=MAX_LENGTH_SUMMARY)
    description: Optional[str] = Field(None, min_length=MIN_LENGTH, max_length=MAX_LENGTH_DESCRIPTION)
    location: Optional[str] = Field(None, min_length=MIN_LENGTH, max_length=MAX_LENGTH_LOCATION)
    itemType: ItemType
    timeSlot: TimeSlotRequest