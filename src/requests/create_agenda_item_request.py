from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from src.constants.validation_contraints import MIN_LENGTH, MAX_LENGTH_LOCATION, MAX_LENGTH_DESCRIPTION, MAX_LENGTH_SUMMARY
from src.enums.item_type import ItemType

class TimeSlotRequest(BaseModel):
    startTime: datetime
    endTime: datetime

class CreateAgendaItemRequest(BaseModel):
    summary: str = Field(..., min_length=MIN_LENGTH, max_length=MAX_LENGTH_SUMMARY)
    description: Optional[str] = Field(None, min_length=MIN_LENGTH, max_length=MAX_LENGTH_DESCRIPTION)
    location: Optional[str] = Field(None, min_length=MIN_LENGTH, max_length=MAX_LENGTH_LOCATION)
    itemType: ItemType
    timeSlot: TimeSlotRequest