import uuid
from typing import Optional

from src.repositories.agenda_repository import AgendaRepository
from src.responses.agenda_response import AgendaResponse
from src.services.agenda_service import AgendaService


class AgendaFacade:
    def __init__(self):
        self.repository = AgendaRepository()
        self.service = AgendaService(self.repository)

    async def initialize(self):
        await self.repository.ensure_table_exists()

    async def list_agenda_items(self, *args, **kwargs):
        return await self.service.list_agenda_items(*args, **kwargs)

    async def get_agenda_item(self, group_id: uuid, item_id: uuid) -> Optional[AgendaResponse]:
        return await self.service.get_agenda_item(group_id, item_id)

    async def create_agenda_item(self, *args, **kwargs):
        return await self.service.create_agenda_item(*args, **kwargs)

    async def update_agenda_item(self, *args, **kwargs):
        return await self.service.update_agenda_item(*args, **kwargs)

    async def delete_agenda_item(self, group_id: uuid, item_id: uuid) -> bool:
        return await self.service.delete_agenda_item(group_id, item_id)
