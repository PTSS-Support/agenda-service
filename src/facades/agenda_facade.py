import uuid
from datetime import datetime
from typing import Optional, List
from azure.data.tables import TableServiceClient
from fastapi import HTTPException
from azure.data.tables.aio import TableClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from src.exceptions.exception_handler import logger
from src.responses.agenda_response import AgendaResponse, TimeSlot, ItemType
from src.exceptions.error_codes import ErrorCode
from src.settings import settings


class AgendaFacade:
    def __init__(self):
        self.table_name = settings.AZURE_STORAGE_TABLE_NAME
        self.table_service_client = TableServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.table_client = TableClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING,
            self.table_name
        )
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Ensure the Azure Table exists, create it if it doesn't."""
        try:
            # One-liner to create table if it doesn't exist
            self.table_service_client.create_table_if_not_exists(self.table_name)
            logger.info(f"Table {self.table_name} ensured.")
        except Exception as e:
            logger.error(f"Error checking or creating table: {e}")
            raise HTTPException(status_code=500, detail="Failed to check or create table")

    import uuid

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

        # Generate a unique RowKey using UUID
        row_key = str(uuid.uuid4())  # Create a UUID as the RowKey

        # Prepare the entity for Azure Table Storage
        entity = {
            "PartitionKey": group_id,
            "RowKey": row_key,  # Use the UUID as RowKey
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
            # Create the entity in Azure Table Storage
            await self.table_client.create_entity(entity=entity)  # Await this call

            # Return the response in the expected format
            return AgendaResponse(
                id=row_key,  # Return the RowKey as the ID
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
        try:
            # Prepare the filter query
            filter_query = f"PartitionKey eq '{group_id}'"
            if start_date:
                start_date_str = start_date.isoformat()
                filter_query += f" and timeSlotEnd ge '{start_date_str}'"
            if end_date:
                end_date_str = end_date.isoformat()
                filter_query += f" and timeSlotStart le '{end_date_str}'"

            # Query the table for items based on the filter query
            entities = self.table_client.query_entities(filter_query)

            # Map the Azure Table entities to the AgendaResponse format
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

        except ResourceNotFoundError:
            raise HTTPException(status_code=404, detail="No agenda items found for the specified group.")
        except Exception as e:
            logger.error(f"Error retrieving agenda items: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve agenda items")