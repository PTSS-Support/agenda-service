from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AgendaQueryParams(BaseModel):
    start_date: Optional[datetime] = Field(
        None,
        alias="startDate",
        description="Start date for filtering agenda items (format: YYYY-MM-DD)",
        examples=["2024-01-17"]
    )
    end_date: Optional[datetime] = Field(
        None,
        alias="endDate",
        description="End date for filtering agenda items (format: YYYY-MM-DD)",
        examples=["2024-12-31"]
    )