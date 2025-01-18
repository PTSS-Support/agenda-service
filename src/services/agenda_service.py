import uuid

from datetime import datetime
from typing import Optional, List
from src.repositories.agenda_repository import AgendaRepository
from src.responses.agenda_response import AgendaResponse, TimeSlot, ItemType
from fastapi import HTTPException
from src.exceptions.error_codes import ErrorCode


class AgendaService:
    def __init__(self, repository: AgendaRepository):
        self.repository = repository

    async def create_agenda_item(
            self,
            group_id: str,
            summary: str,
            description: Optional[str],
            location: Optional[str],
            item_type: ItemType,
            time_slot: TimeSlot
    ) -> AgendaResponse:
        now = datetime.utcnow()
        row_key = str(uuid.uuid4())

        entity = {
            "PartitionKey": group_id,
            "RowKey": row_key,
            "summary": summary,
            "description": description,
            "location": location,
            "itemType": item_type.value,
            "created": now.isoformat(),
            "updated": now.isoformat(),
            "timeSlotStart": time_slot.start.isoformat(),
            "timeSlotEnd": time_slot.end.isoformat()
        }

        try:
            await self.repository.create_entity(entity)
            return AgendaResponse(
                id=row_key,
                summary=summary,
                description=description,
                location=location,
                itemType=item_type,
                created=now,
                updated=now,
                timeSlot=time_slot
            )
        except ResourceExistsError:
            raise HTTPException(
                status_code=ErrorCode.BAD_REQUEST.status,
                detail={
                    "code": ErrorCode.BAD_REQUEST.code,
                    "message": "An agenda item with this identifier already exists"
                }
            )

    async def list_agenda_items(
            self,
            group_id: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> List[AgendaResponse]:
        filter_query = f"PartitionKey eq '{group_id}'"
        if start_date:
            filter_query += f" and timeSlotEnd ge '{start_date.isoformat()}'"
        if end_date:
            filter_query += f" and timeSlotStart le '{end_date.isoformat()}'"

        try:
            entities = await self.repository.query_entities(filter_query)
            agenda_items = []

            async for entity in entities:
                time_slot = TimeSlot(
                    start=datetime.fromisoformat(entity['timeSlotStart']),
                    end=datetime.fromisoformat(entity['timeSlotEnd'])
                )
                agenda_items.append(
                    AgendaResponse(
                        id=entity['RowKey'],
                        summary=entity['summary'],
                        description=entity.get('description'),
                        location=entity.get('location'),
                        itemType=entity['itemType'],
                        created=datetime.fromisoformat(entity['created']),
                        updated=datetime.fromisoformat(entity['updated']),
                        timeSlot=time_slot
                    )
                )
            return agenda_items
        except Exception as e:
            logger.error(f"Error retrieving agenda items: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve agenda items")