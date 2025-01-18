from src.repositories.agenda_repository import AgendaRepository
from src.services.agenda_service import AgendaService


class AgendaFacade:
    def __init__(self):
        self.repository = AgendaRepository()
        self.service = AgendaService(self.repository)

    async def initialize(self):
        await self.repository.ensure_table_exists()

    async def create_agenda_item(self, *args, **kwargs):
        return await self.service.create_agenda_item(*args, **kwargs)

    async def list_agenda_items(self, *args, **kwargs):
        return await self.service.list_agenda_items(*args, **kwargs)