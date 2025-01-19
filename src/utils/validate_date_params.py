from datetime import datetime
from typing import Optional

from fastapi import HTTPException


def validate_date_params(start_date: Optional[datetime], end_date: Optional[datetime]):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before or equal to end date"
        )