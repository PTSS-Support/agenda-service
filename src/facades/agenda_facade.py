from datetime import datetime
from typing import Optional, List
from uuid import UUID

from src.responses.agenda_response import AgendaResponse, ItemType, TimeSlot


class AgendaFacade:
    async def list_agenda_items(
        self,
        group_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AgendaResponse]:
        return [
            AgendaResponse(
                id="test-id",
                summary="Everything went fine",
                description="Test description",
                location="Test location",
                itemType=ItemType.EVENT,
                created=datetime.now(),
                updated=datetime.now(),
                timeSlot=TimeSlot(
                    start=datetime.now(),
                    end=datetime.now()
                )
            )
        ]