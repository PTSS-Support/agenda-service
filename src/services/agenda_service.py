import uuid

from datetime import datetime
from typing import Optional
from azure.core.exceptions import ResourceExistsError
from src.exceptions.exception_handler import logger
from src.repositories.agenda_repository import AgendaRepository
from src.responses.agenda_response import AgendaResponse, TimeSlot, ItemType
from fastapi import HTTPException
from src.exceptions.error_codes import ErrorCode
from src.utils.response_util import map_entity_to_response


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

    async def list_agenda_items(self, group_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):

        filter_query = f"PartitionKey eq '{group_id}'"

        if start_date:
            filter_query += f" and timeSlotEnd ge datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}'"
        if end_date:
            filter_query += f" and timeSlotStart le datetime'{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}'"

        try:
            entities = await self.repository.query_entities(filter_query)
            items = [map_entity_to_response(entity) async for entity in entities]
            return items
        except Exception as e:
            logger.error(f"Error retrieving agenda items: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve agenda items")

    async def get_agenda_item(self, group_id: str, item_id: str):
        filter_query = f"PartitionKey eq '{group_id}' and RowKey eq '{item_id}'"
        try:
            entities = await self.repository.query_entities(filter_query)
            entity = await anext(entities, None)
            return map_entity_to_response(entity) if entity else None
        except Exception as e:
            logger.error(f"Error retrieving agenda item: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve agenda item")

    async def update_agenda_item(
            self,
            group_id: str,
            item_id: str,
            summary: str,
            description: Optional[str],
            location: Optional[str],
            item_type: ItemType,
            time_slot: TimeSlot
    ) -> Optional[AgendaResponse]:
        now = datetime.utcnow()

        existing_item = await self.get_agenda_item(group_id, item_id)
        if not existing_item:
            return None

        entity = {
            "PartitionKey": group_id,
            "RowKey": item_id,
            "summary": summary,
            "description": description,
            "location": location,
            "itemType": item_type.value,
            "created": existing_item.created.isoformat(),
            "updated": now.isoformat(),
            "timeSlotStart": time_slot.start.isoformat(),
            "timeSlotEnd": time_slot.end.isoformat()
        }

        try:
            await self.repository.update_entity(entity)

            return AgendaResponse(
                id=item_id,
                summary=summary,
                description=description,
                location=location,
                itemType=item_type,
                created=existing_item.created,
                updated=now,
                timeSlot=time_slot
            )
        except Exception as e:
            logger.error(f"Error updating agenda item: {e}")
            raise HTTPException(status_code=500, detail="Failed to update agenda item")

    async def delete_agenda_item(self, group_id: uuid, item_id: uuid) -> bool:
        try:
            await self.repository.delete_entity(group_id, item_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting agenda item: {e}")
            return False

