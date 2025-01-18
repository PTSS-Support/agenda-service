from azure.data.tables import TableServiceClient
from azure.data.tables.aio import TableClient
from src.settings import settings
from src.exceptions.exception_handler import logger


class AgendaRepository:
    def __init__(self):
        self.table_name = settings.AZURE_STORAGE_TABLE_NAME
        self.table_service_client = TableServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.table_client = TableClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING,
            self.table_name
        )

    async def ensure_table_exists(self):
        try:
            self.table_service_client.create_table_if_not_exists(self.table_name)
            logger.info(f"Table {self.table_name} ensured.")
        except Exception as e:
            logger.error(f"Error checking or creating table: {e}")
            raise

    async def create_entity(self, entity: dict):
        return await self.table_client.create_entity(entity=entity)

    async def query_entities(self, filter_query: str):
        return self.table_client.query_entities(filter_query)