from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AgendaQueryParams(BaseModel):
    start_date: Optional[datetime] = Field(
        None,
        description="Start date for filtering agenda items (format: YYYY-MM-DD)"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date for filtering agenda items (format: YYYY-MM-DD)"
    )